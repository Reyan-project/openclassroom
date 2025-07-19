python
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import pandas as pd
import os

############## PARAMETRAGE ##############
# 1 = veille_github généraliste, 2 = veille_data data science
MODE = 1
DOSSIER = "projets/veille_metier/veilles"  # Dossier cible pour tous tes fichiers

# Assure la création du dossier si inexistant
os.makedirs(DOSSIER, exist_ok=True)

############## COMMUN ##############
def classify_type_github(description):
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

def classify_type_data(description):
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

def scrape_github_trending(language="python", mode="github"):
    url = f"https://github.com/trending/{language}?since=daily"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    projects = []
    for repo in soup.find_all("article", class_="Box-row")[:50]:
        try:
            repo_name = repo.h2.a.text.strip().replace("\n", "").replace(" ", "")
            owner, name = repo_name.split("/") if "/" in repo_name else ("N/A", repo_name)
            desc_tag = repo.find("p", class_="col-9 color-fg-muted my-1 pr-4")
            description = desc_tag.text.strip() if desc_tag else "Pas de description"
            type_col = (
                classify_type_github(description) if mode == "github" else classify_type_data(description)
            )
            stars_tag = repo.find("span", class_="d-inline-block float-sm-right")
            stars_text = stars_tag.text.strip() if stars_tag else "0"
            stars_number = "".join(c for c in stars_text if c.isdigit())
            projects.append({
                "Langage": language,
                "Nom": name,
                "Description": description,
                "Étoiles": stars_number,
                "Type": type_col,
            })
        except Exception as e:
            print("❌ Erreur dans le parsing d’un dépôt :", e)
    return projects

############## VEILLE GITHUB ##############
def charger_connaissances_perso(fichier):
    try:
        connaissances = pd.read_csv(fichier)
    except FileNotFoundError:
        colonnes = ["Langage", "Nom", "Type", "Description", "Étoiles", "Connu", "Maîtrise", "Priorité_apprentissage", "Objectif_personnel"]
        connaissances = pd.DataFrame(columns=colonnes)
        connaissances.to_csv(fichier, index=False)
    return connaissances.fillna("")

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

def mettre_a_jour_connaissances_perso(nouveaux_resultats, fichier):
    anciens = charger_connaissances_perso(fichier)
    nouveaux = pd.DataFrame(nouveaux_resultats)
    if not nouveaux.empty:
        base = nouveaux[["Langage", "Nom", "Type", "Description", "Étoiles"]].copy()
        base["Connu"] = ""
        base["Maîtrise"] = ""
        base["Priorité_apprentissage"] = ""
        base["Objectif_personnel"] = ""
        fusion = pd.concat([anciens, base], ignore_index=True)
        fusion = fusion.drop_duplicates(subset=["Nom"], keep="first")
        fusion.to_csv(fichier, index=False)
        print(f"🔁 Fichier {fichier} mis à jour avec {len(fusion) - len(anciens)} nouveaux outils.")

############## VEILLE DATA SCIENCE ##############
def charger_connaissances_data(fichier):
    try:
        df = pd.read_csv(fichier)
    except FileNotFoundError:
        colonnes = ["Langage", "Nom", "Type", "Déjà_connu", "Maîtrise", "À_travailler", "Objectif_personnel", "Étoiles", "Date", "Description"]
        df = pd.DataFrame(columns=colonnes)
        df.to_csv(fichier, index=False)
    return df.fillna("")

def enrichir_resultats_data(resultats, connaissances_df, date_str):
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

def mettre_a_jour_connaissances_data(nouveaux_resultats, fichier):
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

############## MAIN FUNCTIONS ##############
def generate_veille_github():
    date_str = datetime.date.today().strftime("%Y-%m")
    filename = f"{DOSSIER}/veille_github_{date_str}.csv"
    base_connaissances = f"{DOSSIER}/connaissances_perso.csv"
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
        projets = scrape_github_trending(key, mode="github")
        for p in projets:
            p["Langage"] = label
            p["Date"] = date_str
            all_results.append(p)
    print(f"📦 {len(all_results)} projets collectés.")
    connaissances_df = charger_connaissances_perso(base_connaissances)
    enriched = enrichir_resultats_avec_priorisation(all_results, connaissances_df)
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
    mettre_a_jour_connaissances_perso(all_results, base_connaissances)

def automatique_veille_data():
    date_str = datetime.date.today().strftime("%Y-%m")
    filename = f"{DOSSIER}/veille_data_{date_str}.csv"
    base_connaissances = f"{DOSSIER}/connaissances_data.csv"
    all_results = []
    topics = {
        "python": "Python",
        "jupyter-notebook": "Jupyter",
    }
    for key, label in topics.items():
        projets = scrape_github_trending(key, mode="data")
        for p in projets:
            p["Langage"] = label
            all_results.append(p)
    connaissances_df = charger_connaissances_data(base_connaissances)
    enriched = enrichir_resultats_data(all_results, connaissances_df, date_str)
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
    mettre_a_jour_connaissances_data(enriched, base_connaissances)

############## ENTRYPOINT ##############
if __name__ == "__main__":
    if MODE == 1:
        generate_veille_github()
    else:
        automatique_veille_data()
