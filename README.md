# Taskboard
Projet DevSecOps Yassine Vadim Yvan

## Revue IA des pull requests

À l'ouverture ou à la réouverture d'une pull request, puis à chaque nouveau
commit poussé sur celle-ci, GitHub Actions demande une revue du diff à Gemini
et publie le résultat comme commentaire de revue sur la PR en mentionnant son
auteur. Une nouvelle revue est publiée à chaque déclenchement.

Pour activer l'intégration :

1. Créez une clé API dans [Google AI Studio](https://aistudio.google.com/apikey).
2. Ajoutez-la dans **Settings > Secrets and variables > Actions** sous le nom
   `GEMINI_API_KEY`.
3. Vérifiez que les GitHub Actions sont autorisées à créer des revues de PR
   dans les paramètres du dépôt.

Le modèle par défaut est `gemini-2.5-flash`. Le workflow utilise
`pull_request_target` pour fonctionner aussi sur les PR provenant de forks ;
il récupère uniquement le script de la branche de base et analyse le diff via
l'API GitHub, sans exécuter le code de la PR. Le diff est transmis à Google
Gemini pour analyse.
