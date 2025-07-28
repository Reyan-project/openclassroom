# Projet Portfolio Data - Veille Technologique & Data Science Automatisée

## 💼 Contexte du projet

Ce projet a pour but de démontrer ma capacité à mener une **veille technologique automatisée** et une veille spécifique en **Data Science**, avec un pipeline complet :  
- collecte automatique de données sur GitHub trending,  
- enrichissement avec mes connaissances personnelles,  
- structuration des résultats dans des fichiers CSV,  
- préparation pour création de tableaux de bord ou analyses ultérieures.

Ce travail est présenté sous forme de script Python exécuté automatiquement, prêt à être intégré dans un portfolio GitHub professionnel pour valoriser mes compétences en data, automatisation et gestion de projet.

---

## 🎯 Objectifs métier

- Automatiser la récupération et le suivi des tendances dans les bibliothèques et outils de développement (généraliste et data science).  
- Garder trace de mes connaissances déjà acquises, en priorisant les outils à apprendre.  
- Générer des fichiers structurés, prêts à être exploités dans des tableaux de bord ou analyses de progression.  
- Illustrer ma maîtrise des bonnes pratiques Python, de la collecte web (scraping), de la manipulation data avec pandas, et de la gestion de fichiers CSV.

---

## 🔧 Description technique - Fonctionnement du script principal

### Paramètres

- `MODE` : Choix du type de veille à exécuter  
  - `1` = Veille GitHub généraliste (outils divers)  
  - `2` = Veille Data Science spécifique  
  - `3` = Exécute les deux veilles successivement  

- `DOSSIER` : Dossier relatif à la racine du projet où les fichiers de résultats et bases de connaissances sont stockés automatiquement  
Ex: `projets/veille_metier/veilles/`

---

### Étapes du script :

1. **Collecte des projets trending sur GitHub**  
   Le script récupère les 50 projets du jour par langage/topic via scraping de [GitHub Trending](https://github.com/trending).

2. **Classification automatique**  
   Chaque projet est analysé pour déterminer son type (Web, API, Data, NLP, ML, etc.) selon des mots-clés dans la description, avec deux modes selon la veille sélectionnée.

3. **Enrichissement des données**  
   Les nouveaux projets sont comparés aux fichiers de connaissances personnelles (`connaissances_perso.csv` et `connaissances_data.csv`). Cette étape marque si un outil est déjà connu, maîtrisé ou à étudier.

4. **Génération des fichiers CSV de veille**  
   Un fichier CSV mensuel est sauvegardé dans le dossier cible avec la liste actualisée des projets trending, enrichie des statuts personnalisés.

5. **Mise à jour des bases de connaissances**  
   Les fichiers de suivi personnels sont mis à jour pour incorporer les nouveaux outils détectés.

---

## 🔍 Technologies utilisées

- **Python 3** pour toute la programmation  
- Librairies :  
  - `requests` (requêtes HTTP)  
  - `BeautifulSoup` (scraping HTML)  
  - `pandas` (gestion et manipulation des données)  
  - `csv` (lecture/écriture fichiers CSV)  
  - `os` (gestion dossiers/fichiers)
  
---

## 🚀 Comment utiliser ce projet


1. Installer les dépendances :  pip install requests beautifulsoup4 pandas csv os 

2. Configurer le `MODE` dans le script pour choisir la veille désirée (1, 2 ou 3).

3. Lancer le script Python :  python projets/veille_metier/veille.py

4. Tous les fichiers seront générés dans le dossier `projets/veille_metier/veilles`.
