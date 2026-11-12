import json
import os
import tempfile
import unittest
from unittest.mock import patch

from scripts import ai_pr_review


class TeamReviewerRequestTests(unittest.TestCase):
    def setUp(self):
        self.api_url = "https://api.github.com"
        self.repository = "example/taskboard"
        self.number = 12
        self.headers = {"Authorization": "Bearer test-token"}

    @patch("scripts.ai_pr_review.request")
    def test_opened_pr_requests_the_other_team_members(self, request):
        pull_request = {
            "user": {"login": "vadimbrsn"},
            "requested_reviewers": [],
        }

        ai_pr_review.request_team_reviewers(
            self.api_url,
            self.repository,
            self.number,
            self.headers,
            "opened",
            pull_request,
        )

        request.assert_called_once_with(
            "https://api.github.com/repos/example/taskboard/pulls/12/"
            "requested_reviewers",
            self.headers,
            {"reviewers": ["yass95-collab", "Yvan134"]},
            retries=2,
        )

    @patch("scripts.ai_pr_review.request")
    def test_synchronize_does_not_send_another_review_request(self, request):
        ai_pr_review.request_team_reviewers(
            self.api_url,
            self.repository,
            self.number,
            self.headers,
            "synchronize",
            {"user": {"login": "vadimbrsn"}},
        )

        request.assert_not_called()

    @patch("scripts.ai_pr_review.request")
    def test_reopened_pr_skips_reviewers_already_requested(self, request):
        pull_request = {
            "user": {"login": "vadimbrsn"},
            "requested_reviewers": [{"login": "yass95-collab"}],
        }

        ai_pr_review.request_team_reviewers(
            self.api_url,
            self.repository,
            self.number,
            self.headers,
            "reopened",
            pull_request,
        )

        request.assert_called_once_with(
            "https://api.github.com/repos/example/taskboard/pulls/12/"
            "requested_reviewers",
            self.headers,
            {"reviewers": ["Yvan134"]},
            retries=2,
        )


class ReviewContextTests(unittest.TestCase):
    def test_main_sends_pr_metadata_and_project_guidelines_to_gemini(self):
        event = {
            "repository": {"full_name": "example/taskboard"},
            "pull_request": {
                "number": 11,
                "user": {"login": "contributor"},
                "head": {"sha": "abc123"},
                "title": "Add a health endpoint",
                "body": "The readiness endpoint checks the database.",
            },
        }
        calls = []

        def fake_request(url, headers, payload=None, retries=0):
            calls.append((url, payload))
            if url.endswith("/pulls/11") and payload is None:
                return (
                    b"diff --git a/app/server.py b/app/server.py\n"
                    b"+def healthz(): return 200\n"
                )
            if "generateContent" in url:
                return json.dumps(
                    {
                        "candidates": [
                            {
                                "content": {
                                    "parts": [{"text": "No actionable findings."}]
                                }
                            }
                        ]
                    }
                ).encode()
            return b"{}"

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        ) as event_file:
            json.dump(event, event_file)
            event_path = event_file.name

        try:
            with patch.dict(
                os.environ,
                {
                    "GITHUB_TOKEN": "test-token",
                    "GEMINI_API_KEY": "test-key",
                    "GITHUB_EVENT_PATH": event_path,
                },
                clear=False,
            ), patch.object(ai_pr_review, "request", side_effect=fake_request):
                ai_pr_review.main()
        finally:
            os.unlink(event_path)

        model_call = next(call for call in calls if "generateContent" in call[0])
        prompt = model_call[1]["contents"][0]["parts"][0]["text"]
        system_instruction = model_call[1]["systemInstruction"]["parts"][0]["text"]
        review_payload = calls[-1][1]

        self.assertIn("TaskBoard project review guidelines", prompt)
        self.assertIn("Add a health endpoint", prompt)
        self.assertIn("The readiness endpoint checks the database.", prompt)
        self.assertIn("diff --git a/app/server.py", prompt)
        self.assertIn("untrusted data", system_instruction)
        self.assertIn("write in English", system_instruction)
        self.assertEqual(review_payload["commit_id"], "abc123")
        self.assertIn("## AI Review", review_payload["body"])
        self.assertIn("No actionable findings.", review_payload["body"])


if __name__ == "__main__":
    unittest.main()
