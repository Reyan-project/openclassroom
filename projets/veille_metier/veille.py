import requests
from bs4 import BeautifulSoup
import csv
import datetime
import pandas as pd


# 🔁 Charger ton fichier connaissances_perso.csv
def charger_connaissances_perso(fichier="connaissances_perso.csv"):
    try:
        connaissances = pd.read_csv(fichier)
    except FileNotFoundError:
        # S'il n'existe pas, on crée un fichier vide avec les colonnes attendues
        colonnes = ["Langage", "Nom", "Type", "Description", "Étoiles",
                    "Connu", "Maîtrise", "Priorité_apprentissage", "Objectif_personnel"]
        connaissances = pd.DataFrame(columns=colonnes)
        connaissances.to_csv(fichier, index=False)
    return connaissances.fillna("")


# 🧠 Marquer chaque projet en fonction de tes connaissances
def enrichir_resultats_avec_priorisation(resultats, connaissances_df):
    nouveaux_resultats = []
    for res in resultats:
        nom = res["Nom"].lower()
        ligne = connaissances_df[connaissances_df["Nom"].str.lower() == nom]
        if not ligne.empty:
            res["Déjà_connu"] = ligne.iloc[0]["Connu"]
            res["Maîtrise"] = ligne.iloc[0]["Maîtrise"]
            res["À_travailler"] = ligne.iloc[0]["Priorité_apprentissage"]
            res["Objectif_personnel"] = ligne.iloc[0]["Objectif_personnel"]
        else:
            res["Déjà_connu"] = "non"
            res["Maîtrise"] = "non"
            res["À_travailler"] = "oui"
            res["Objectif_personnel"] = "Découvrir"
        nouveaux_resultats.append(res)
    return nouveaux_resultats


# 🎯 Classer automatiquement par type (Web, API…)
def classify_type(description):
    if not description:
        return "Autre"
    desc = description.lower()
    keywords = {
        "Web": ["web", "browser", "html", "css", "javascript", "frontend", "site", "framework"],
        "API": ["api", "rest", "endpoint", "client", "server", "proxy", "gateway"],
        "NLP": ["language model", "llm", "nlp", "bert", "gpt", "transformer", "text", "token", "question answering", "summarization"],
        "Data": ["data", "dataset", "dataframe", "database", "etl", "csv", "analytics", "visualization", "chart", "parquet"],
        "ML": ["machine learning", "ml", "deep learning", "ai", "neural", "learning", "trainer", "classifier", "model", "inference"]
    }
    for t, kwds in keywords.items():
        if any(k in desc for k in kwds):
            return t
    return "Autre"


# 📤 Scraping GitHub Trending
def scrape_github_trending(language="python"):
    url = f"https://github.com/trending/{language}?since=daily"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    projects = []

    for repo in soup.find_all('article', class_='Box-row')[:50]:
        try:
            repo_name = repo.h2.a.text.strip().replace("\n", "").replace(" ", "")
            owner, name = repo_name.split('/') if '/' in repo_name else ("N/A", repo_name)
            desc_tag = repo.find('p', class_='col-9 color-fg-muted my-1 pr-4')
            description = desc_tag.text.strip() if desc_tag else "Pas de description"
            type_col = classify_type(description)
            stars_tag = repo.find('span', class_='d-inline-block float-sm-right')
            stars_text = stars_tag.text.strip() if stars_tag else "0"
            stars_number = ''.join(c for c in stars_text if c.isdigit())

            projects.append({
                'Langage': language,
                'Nom': name,
                'Description': description,
                'Étoiles': stars_number,
                'Type': type_col
            })
        except Exception as e:
            print("❌ Erreur dans le parsing d’un dépôt :", e)
    return projects


# 🔁 Mise à jour automatique du fichier connaissances_perso.csv
def mettre_a_jour_connaissances_perso(nouveaux_resultats, fichier="connaissances_perso.csv"):
    anciens = charger_connaissances_perso(fichier)
    nouveaux = pd.DataFrame(nouveaux_resultats)
    if not nouveaux.empty:
        base = nouveaux[["Langage", "Nom", "Type", "Description", "Étoiles"]].copy()
        base["Connu"] = ""
        base["Maîtrise"] = ""
        base["Priorité_apprentissage"] = ""
        base["Objectif_personnel"] = ""
        fusion = pd.concat([anciens, base], ignore_index=True)
        fusion = fusion.drop_duplicates(subset=['Nom'], keep='first')
        fusion.to_csv(fichier, index=False)
        print(f"🔁 Fichier {fichier} mis à jour avec {len(fusion) - len(anciens)} nouveaux outils.")
    else:
        print("Aucun outil à ajouter à la base de connaissances.")


# 🚀 Génération de la veille + mise à jour connaissances
def generate_veille_github():
    date_str = datetime.date.today().strftime("%Y-%m")
    filename = f"veille_github_{date_str}.csv"

    all_results = []

    topics = {
        "python": "Python",
        "javascript": "JavaScript",
        "rust": "Rust",
        "go": "Go",
        "typescript": "TypeScript",
        "java": "Java",
        "jupyter-notebook": "Jupyter",
        "machine-learning": "Machine Learning",
        "deep-learning": "Deep Learning",
    }

    print("📡 Scraping GitHub Trending en cours...")

    for key, label in topics.items():
        projets = scrape_github_trending(key)
        for p in projets:
            p["Langage"] = label
            p["Date"] = date_str
            all_results.append(p)

    print(f"📦 {len(all_results)} projets collectés.")

    # Charger les connaissances
    connaissances_df = charger_connaissances_perso()

    # Enrichir les résultats
    enriched = enrichir_resultats_avec_priorisation(all_results, connaissances_df)

    # Enregistrer le fichier de veille du mois
    fieldnames = [
        "Langage", "Nom", "Type", "Déjà_connu", "Maîtrise",
        "À_travailler", "Objectif_personnel", "Étoiles", "Date", "Description"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in enriched:
            writer.writerow(row)

    print(f"✅ Fichier veille enregistré : {filename}")

    # Mise à jour connaissances_perso.csv
    mettre_a_jour_connaissances_perso(all_results)


# ▶️ Lancer tout automatiquement
if __name__ == "__main__":
    generate_veille_github()


import requests
from bs4 import BeautifulSoup
import csv
import datetime
import pandas as pd

# Charger le fichier compétences perso ou créer un vide
def charger_connaissances_data(fichier='connaissances_data.csv'):
    try:
        df = pd.read_csv(fichier)
    except FileNotFoundError:
        colonnes = ["Langage", "Nom", "Type", "Déjà_connu", "Maîtrise", "À_travailler", "Objectif_personnel", "Étoiles", "Date", "Description"]
        df = pd.DataFrame(columns=colonnes)
        df.to_csv(fichier, index=False)
    return df.fillna("")

# Classifier Data Science/DataViz/ML/NLP en fonction de la description
def classify_type(description):
    if not description:
        return "Autre"
    desc = description.lower()
    keywords = {
        "Data": ["data", "dataset", "dataframe", "etl", "csv", "parquet", "panda", "dplyr", "tidyverse"],
        "DataViz": ["visualization", "viz", "plot", "matplotlib", "seaborn", "chart", "graph", "bokeh", "plotly"],
        "ML": ["machine learning", "ml", "deep learning", "ai", "neural", "regression", "classification", "feature", "predict"],
        "NLP": ["nlp", "text", "language", "bert", "llm", "transformer", "gpt", "token", "embedding"],
    }
    for t, kwds in keywords.items():
        if any(k in desc for k in kwds):
            return t
    return "Autre"

# Scraper GitHub Trending pour langages Data Science
def scrape_github_trending(language="python"):
    url = f"https://github.com/trending/{language}?since=daily"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    projects = []
    for repo in soup.find_all('article', class_='Box-row')[:50]:
        try:
            repo_name = repo.h2.a.text.strip().replace("\n", "").replace(" ", "")
            owner, name = repo_name.split('/') if '/' in repo_name else ("N/A", repo_name)
            desc_tag = repo.find('p', class_='col-9 color-fg-muted my-1 pr-4')
            description = desc_tag.text.strip() if desc_tag else "Pas de description"
            type_col = classify_type(description)
            stars_tag = repo.find('span', class_='d-inline-block float-sm-right')
            stars_text = stars_tag.text.strip() if stars_tag else "0"
            stars_number = ''.join(c for c in stars_text if c.isdigit())
            projects.append({
                'Langage': language,
                'Nom': name,
                'Description': description,
                'Étoiles': stars_number,
                'Type': type_col
            })
        except Exception as e:
            print("Erreur dépôt :", e)
    return projects

# Enrichir avec compétences perso
def enrichir_resultats_avec_priorisation(resultats, connaissances_df, date_str):
    nouveaux_resultats = []
    for res in resultats:
        nom = res["Nom"].lower()
        ligne = connaissances_df[connaissances_df["Nom"].str.lower() == nom]
        res["Date"] = date_str
        if not ligne.empty:
            res["Déjà_connu"] = ligne.iloc[0]["Déjà_connu"]
            res["Maîtrise"] = ligne.iloc[0]["Maîtrise"]
            res["À_travailler"] = ligne.iloc[0]["À_travailler"]
            res["Objectif_personnel"] = ligne.iloc[0]["Objectif_personnel"]
        else:
            res["Déjà_connu"] = ""
            res["Maîtrise"] = ""
            res["À_travailler"] = "oui"
            res["Objectif_personnel"] = ""
        nouveaux_resultats.append(res)
    return nouveaux_resultats

# Mettre à jour automatiquement le référentiel
def mettre_a_jour_connaissances_data(nouveaux_resultats, fichier="connaissances_data.csv"):
    colonnes = [
        "Langage", "Nom", "Type", "Déjà_connu", "Maîtrise", "À_travailler",
        "Objectif_personnel", "Étoiles", "Date", "Description"
    ]
    try:
        ancien_df = pd.read_csv(fichier)
    except FileNotFoundError:
        ancien_df = pd.DataFrame(columns=colonnes)
    nouveaux_df = pd.DataFrame(nouveaux_resultats)
    for col in colonnes:
        if col not in nouveaux_df.columns:
            nouveaux_df[col] = ""
    nouveaux_df = nouveaux_df[colonnes]
    fusion_df = pd.concat([ancien_df, nouveaux_df], ignore_index=True)
    fusion_df = fusion_df.drop_duplicates(subset=["Nom"], keep="first")
    fusion_df.to_csv(fichier, index=False)
    print(f"🔁 Fichier {fichier} mis à jour.")

# Fonction principale
def automatique_veille_data():
    date_str = datetime.date.today().strftime("%Y-%m")
    filename = f"veille_data_{date_str}.csv"
    all_results = []
    topics = {
        "python": "Python",
        "r": "R",
        "julia": "Julia",
        "jupyter-notebook": "Jupyter",
    }
    for key, label in topics.items():
        projets = scrape_github_trending(key)
        for p in projets:
            p["Langage"] = label
            all_results.append(p)
    connaissances_df = charger_connaissances_data()
    enriched = enrichir_resultats_avec_priorisation(all_results, connaissances_df, date_str)
    # Générer le CSV du mois
    fieldnames = [
        "Langage", "Nom", "Type", "Déjà_connu", "Maîtrise", "À_travailler",
        "Objectif_personnel", "Étoiles", "Date", "Description"
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in enriched:
            writer.writerow(row)
    print(f"✅ Fichier veille mensuelle : {filename}")
    mettre_a_jour_connaissances_data(enriched)

if __name__ == "__main__":
    automatique_veille_data()