# Taskboard
Projet DevSecOps Yassine Vadim Yvan

## Revue IA des pull requests

À l'ouverture ou à la réouverture d'une pull request, puis à chaque nouveau
commit poussé sur celle-ci, GitHub Actions demande une revue du diff à Gemini
et publie le résultat comme commentaire de revue sur la PR en mentionnant son
auteur. Une nouvelle revue est publiée à chaque déclenchement.
À l'ouverture ou à la réouverture, le workflow demande aussi une revue aux
autres membres de l'équipe (`yass95-collab`, `vadimbrsn`, `Yvan134`) en excluant
l'auteur de la PR ; cette demande n'est pas répétée à chaque nouveau commit.
Les commentaires de revue sont rédigés en anglais.

Pour activer l'intégration :

1. Créez une clé API dans [Google AI Studio](https://aistudio.google.com/apikey).
2. Ajoutez-la dans **Settings > Secrets and variables > Actions** sous le nom
   `GEMINI_API_KEY`.
3. (Facultatif) Ajoutez une variable Actions nommée `GEMINI_MODEL` pour choisir
   le modèle. La valeur par défaut est `gemini-3.8-flash`. Pour essayer une
   alternative Flash-Lite, utilisez `gemini-3.5-flash-lite`.
4. Vérifiez que les GitHub Actions sont autorisées à créer des revues de PR
   dans les paramètres du dépôt.

Le modèle par défaut est `gemini-3.8-flash`. Les erreurs temporaires de l'API
(408, 429, 5xx et erreurs réseau) déclenchent jusqu'à quatre nouvelles
tentatives avec délai exponentiel (1, 2, 4, 8 secondes) et jitter, plafonné à
60 secondes. Les erreurs client comme 400 ou 403 ne sont pas réessayées. La
revue limite sa réponse à 2048 tokens pour réduire le travail de génération.

Le workflow utilise `pull_request_target` pour fonctionner aussi sur les PR
provenant de forks ; il récupère uniquement le script de la branche de base et
analyse le diff via l'API GitHub, sans exécuter le code de la PR. Le diff est
transmis à Google Gemini pour analyse.
