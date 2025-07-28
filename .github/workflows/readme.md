# Veille Automatique Mensuelle - Workflow GitHub Actions

## 📋 Contexte et objectif

Ce projet met en place une **veille technologique automatisée mensuelle** avec GitHub Actions.  
Chaque premier du mois à 6h05 UTC, un script Python est exécuté pour collecter les projets trending sur GitHub, enrichir la base de connaissances personnelle, générer des fichiers CSV de veille et les stocker dans le dépôt.

L'objectif est de centraliser et automatiser le suivi des tendances technologiques, facilitant le suivi régulier, l’analyse, et la constitution d’un portfolio data professionnel.

---

## ⚙️ Description du workflow GitHub Actions

Le workflow est défini dans `.github/workflows/veille.yml` et comprend les étapes suivantes :

### Déclenchement

- Automatique : chaque premier du mois à 6h05 UTC (config. CRON `5 6 1 * *`)
- Manuel : possibilité de déclenchement via interface GitHub (“workflow_dispatch”)

### Jobs et étapes

- **Clonage** du dépôt
- **Vérifications initiales** (listing des fichiers pour debug)
- **Installation** des dépendances Python (`requests`, `beautifulsoup4`, `pandas`, `jupyter`)
- **Création** du dossier cible `projets/veille_metier/veilles` si inexistant
- **Exécution du script Python** de veille `veille.py`
- **Listing** complet des fichiers générés pour vérification
- **Déplacement manuel** des fichiers veille (au cas où le script génère hors dossier cible)
- **Gestion Git** : commit & push automatique des fichiers dans le dossier veille, avec gestion conditionnelle quand il y a des fichiers à ajouter

---

## 🔧 Détails techniques

- Le script Python `veille.py` produit les fichiers CSV mensuels (`veille_github_YYYY-MM.csv`, `veille_data_YYYY-MM.csv`) ainsi que les bases de connaissances (`connaissances_perso.csv`, `connaissances_data.csv`).
- Les fichiers sont stockés dans `projets/veille_metier/veilles` pour organiser proprement les données.
- Le push remonte automatiquement à la branche principale en gérant les éventuels conflits via un `git pull --rebase`.

## Prochaine étapes envisagé mettre en place de l'IA pour donnée plus pertinentes
