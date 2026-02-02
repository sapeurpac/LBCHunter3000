# 🕵️‍♂️ LBC Hunter 3000

**LBC Hunter 3000** est un outil de veille et d'analyse automatisé pour LeBonCoin, spécialisé dans la recherche de matériel informatique (PC Gamer, Cartes Graphiques, Processeurs, etc.).

Il combine un **Scraper intelligent** (Playwright) capable d'extraire les spécifications techniques (RAM, SSD, GPU...) via des Regex, et un **Dashboard interactif** (Streamlit) pour visualiser les prix, filtrer les annonces et détecter les bonnes affaires.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Playwright](https://img.shields.io/badge/Playwright-Scraping-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

## 🚀 Fonctionnalités

* **Scraping Rapide ("Fail Fast")** : Utilise Playwright en mode synchrone optimisé (blocage des images/fonts) pour une vitesse maximale.
* **Analyse Sémantique** : Le script `analyser.py` lit le titre et la description pour extraire automatiquement :
    * CPU (Intel Core / AMD Ryzen)
    * GPU (Modèle + VRAM)
    * RAM (Quantité + Type DDR)
    * Stockage (Distinction SSD vs HDD)
    * État du produit (Neuf, Bon état, HS...)
* **Anti-Doublons** : Gestion intelligente via SQLite. Si une annonce existe déjà, elle n'est pas réimportée.
* **Dashboard Visuel** :
    * Graphiques de distribution des prix.
    * Filtres dynamiques (Budget, GPU, RAM).
    * Tableau interactif avec liens directs.
    <img width="1885" height="832" alt="image" src="https://github.com/user-attachments/assets/0e5ab51d-ad8b-4902-aee0-c0fff9929651" />

* **Architecture Robuste** : Le scraper tourne dans un processus isolé (`subprocess`) pour éviter les crashs de l'interface graphique.

## 🛠️ Installation

1.  **Cloner le projet**
    ```bash
    git clone [https://github.com/votre-pseudo/lbc-hunter-3000.git](https://github.com/votre-pseudo/lbc-hunter-3000.git)
    cd lbc-hunter-3000
    ```

2.  **Créer un environnement virtuel (recommandé)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Installer les navigateurs Playwright**
    ```bash
    playwright install chromium
    ```

## 📦 Contenu du fichier `requirements.txt`
Si vous n'avez pas le fichier, créez-le avec ceci :
```text
streamlit
pandas
playwright
```

## 🛠️ Execution du script :
  ```bash
    streamlit run dashboard.py
    ```
