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


if __name__ == "__main__":
    unittest.main()
