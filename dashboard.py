# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import time
import subprocess
import sys
import database

# Configuration de la page
st.set_page_config(page_title="LBC Hunter 3000", layout="wide", page_icon="🕵️‍♂️")

# Initialisation BDD
database.init_db()

# =========================================================
# 🏗️ FONCTIONS UTILITAIRES
# =========================================================
def get_data():
    """Récupère les données fraîches de la BDD"""
    conn = sqlite3.connect("leboncoin.db")
    try:
        df = pd.read_sql_query("SELECT * FROM annonces ORDER BY date_ajout DESC", conn)
        conn.close()
        return df
    except:
        conn.close()
        return pd.DataFrame()

# =========================================================
# 🚀 SIDEBAR : LE CENTRE DE COMMANDE
# =========================================================
st.sidebar.title("🤖 Lancer le Crawler")
st.sidebar.markdown("---")

search_query = st.sidebar.text_input("Objet à rechercher", placeholder="Ex: RTX 4070, iPhone 15...")

if st.sidebar.button("🚀 Lancer la recherche", type="primary"):
    if not search_query:
        st.sidebar.error("Veuillez entrer un mot clé.")
    else:
        status_placeholder = st.sidebar.empty()
        status_placeholder.info(f"🔍 Démarrage du scraping pour '{search_query}'...")
        
        with st.spinner('Le robot travaille dans une autre fenêtre...'):
            try:
                # --- MODIFICATION MAJEURE ICI ---
                # On lance scraper.py comme un processus indépendant
                # sys.executable assure qu'on utilise le python du venv actuel
                result = subprocess.run(
                    [sys.executable, "scraper.py", search_query], 
                    capture_output=True, 
                    text=True,
                    encoding='utf-8' # Force l'encodage pour éviter les erreurs d'accents
                )
                
                # On vérifie si le script a planté
                if result.returncode != 0:
                    st.sidebar.error("Erreur lors de l'exécution du script.")
                    st.sidebar.code(result.stderr) # Affiche l'erreur technique
                else:
                    # On récupère le chiffre affiché par le print() du scraper
                    try:
                        nb_new = int(result.stdout.strip().split('\n')[-1])
                        status_placeholder.success("Terminé !")
                        
                        if nb_new > 0:
                            st.sidebar.success(f"✅ {nb_new} nouvelles annonces ajoutées !")
                        else:
                            st.sidebar.warning("Aucune nouvelle annonce trouvée.")
                        
                        time.sleep(2)
                        st.rerun()
                    except ValueError:
                        st.sidebar.warning("Le scraper a fini mais n'a pas renvoyé de chiffre valide.")
                        # Afficher la sortie pour débugger si besoin
                        with st.expander("Voir les logs du scraper"):
                            st.code(result.stdout)

            except Exception as e:
                st.sidebar.error(f"Erreur système : {e}")

st.sidebar.markdown("---")
st.sidebar.info("💡 Astuce : Une fenêtre Chrome va s'ouvrir indépendamment.")

# =========================================================
# 📊 MAIN : LE TABLEAU DE BORD
# =========================================================

st.title("📊 Dashboard des Annonces")

df = get_data()

if df.empty:
    st.info("👋 Bienvenue ! La base de données est vide. Lancez une recherche à gauche.")
else:
    with st.expander("🔎 Filtres Avancés", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            min_p, max_p = int(df['prix'].min()), int(df['prix'].max())
            if min_p == max_p: max_p += 100
            prix_range = st.slider("Budget (€)", min_p, max_p, (min_p, max_p))
        
        with col_f2:
            gpu_list = [x for x in df['gpu'].unique() if x and x != "Non spécifié"]
            gpu_select = st.multiselect("Carte Graphique", options=gpu_list, default=gpu_list)
        
        with col_f3:
            ram_list = sorted([x for x in df['ram'].unique() if pd.notnull(x)])
            ram_select = st.multiselect("RAM (Go)", options=ram_list, default=ram_list)

    mask = (df['prix'] >= prix_range[0]) & (df['prix'] <= prix_range[1])
    if gpu_select: mask = mask & df['gpu'].isin(gpu_select)
    if ram_select: mask = mask & df['ram'].isin(ram_select)
    
    df_filtered = df[mask]

    st.markdown("### 📈 Vue d'ensemble")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Annonces filtrées", len(df_filtered))
    mean_price = int(df_filtered['prix'].mean()) if not df_filtered.empty else 0
    kpi2.metric("Prix Moyen", f"{mean_price} €")
    min_price = int(df_filtered['prix'].min()) if not df_filtered.empty else 0
    kpi3.metric("Prix Minimum", f"{min_price} €")
    nb_neuf = len(df_filtered[df_filtered['etat'].str.contains("Neuf|Scellé", case=False, na=False)]) if not df_filtered.empty else 0
    kpi4.metric("Produits Neufs", nb_neuf)

    col_chart1, col_chart2 = st.columns([2, 1])
    with col_chart1:
        if not df_filtered.empty: st.bar_chart(df_filtered.set_index('titre')['prix'])
    with col_chart2:
        if not df_filtered.empty: st.bar_chart(df_filtered['etat'].value_counts())

    st.subheader("📋 Détails des annonces")
    
    column_config = {
        "url": st.column_config.LinkColumn("Lien", display_text="Voir"),
        "prix": st.column_config.NumberColumn("Prix", format="%d €"),
        "ssd": st.column_config.NumberColumn("SSD", format="%d Go"),
        "hdd": st.column_config.NumberColumn("HDD", format="%d Go"),
        "ram": st.column_config.NumberColumn("RAM", format="%d Go"),
        "gpu_vram": st.column_config.TextColumn("VRAM"),
        "description": st.column_config.TextColumn("Description", width="small")
    }
    
    # Nouvelles colonnes à afficher
    cols_to_show = ['titre', 'prix', 'etat', 'gpu', 'gpu_vram', 'cpu', 'ram', 'ssd', 'hdd', 'ville', 'url']
    
    cols_exist = [c for c in cols_to_show if c in df_filtered.columns]

    st.dataframe(
        df_filtered[cols_exist], 
        column_config=column_config, 
        width="stretch", 
        hide_index=True
    )