# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import time
import subprocess
import sys
import database

# =========================================================
# 💠 CONFIGURATION HYBRIDE (CYBER-CLEAN)
# =========================================================
st.set_page_config(
    page_title="LBC HUNTER [SYS]",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="collapsed"
)

# Initialisation BDD
database.init_db()

# =========================================================
# 🎨 STYLE CSS "CYBERPUNK CORPORATE" + ANIMATION TITRE
# =========================================================
st.markdown("""
<style>
    /* 1. IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    /* IMPORT DE TA POLICE VARIABLE (META) */
    @font-face {
        src: url("https://www.axis-praxis.org/fonts/webfonts/MetaVariableDemo-Set.woff2") format("woff2");
        font-family: "Meta";
        font-style: normal;
        font-weight: normal;
    }

    :root {
        --bg-dark: #0a0e17;
        --glass-dark: rgba(20, 30, 48, 0.6);
        --neon-cyan: #00F3FF;
        --neon-purple: #BC13FE;
        --text-main: #E0E6ED;
        --border-color: rgba(0, 243, 255, 0.3);
    }

    /* 2. BACKGROUND GLOBAL */
    .stApp {
        background-color: var(--bg-dark);
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(188, 19, 254, 0.05), transparent 25%), 
            radial-gradient(circle at 85% 30%, rgba(0, 243, 255, 0.05), transparent 25%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    /* 3. ANIMATION DU TITRE (Adaptation de ton code) */
    .title-anim {
        font-family: "Meta", sans-serif;
        font-size: 5rem; /* Ajusté pour le dashboard */
        text-align: center;
        color: transparent;
        -webkit-text-stroke: 2px #E0E6ED; /* Bordure blanche/grise */
        font-variation-settings: "wght" 900, "ital" 1;
        cursor: pointer;
        transition: all 0.5s ease;
        line-height: 1.2;
        margin-bottom: 40px;
        
        /* Ombres adaptées aux couleurs du thème (Cyan -> Violet -> Dark) */
        text-shadow: 
            6px 6px 0px var(--neon-cyan),
            12px 12px 0px var(--neon-purple),
            18px 18px 0px #482896;
    }

    .title-anim:hover {
        font-variation-settings: "wght" 100, "ital" 0;
        text-shadow: none;
        -webkit-text-stroke: 2px var(--neon-cyan);
        color: rgba(0, 243, 255, 0.1);
    }

    /* 4. CONTAINERS (LES "CARTES") */
    .cyber-card {
        background: var(--glass-dark);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .cyber-card:hover {
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
        border-color: var(--neon-cyan);
    }

    /* 5. TYPOGRAPHIE SECONDAIRE */
    h2, h3 {
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
        color: var(--neon-cyan) !important;
    }
    
    /* 6. INPUTS & SELECTBOX */
    .stTextInput input, .stNumberInput input, .stMultiSelect {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--neon-cyan) !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 4px !important;
    }
    .stTextInput input:focus {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
    }

    /* 7. BOUTONS */
    .stButton button {
        background: transparent !important;
        border: 1px solid var(--neon-cyan) !important;
        color: var(--neon-cyan) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border-radius: 4px !important;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: var(--neon-cyan) !important;
        color: #000 !important;
        box-shadow: 0 0 20px var(--neon-cyan);
    }

    /* 8. CONSOLE LOGS */
    .console-box {
        background-color: #050505;
        border-left: 3px solid var(--neon-cyan);
        color: #a0a0a0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        padding: 15px;
        height: 250px;
        overflow-y: auto;
        border-radius: 0 8px 8px 0;
    }
    .log-line { margin-bottom: 5px; }
    .log-success { color: var(--neon-cyan); }
    .log-error { color: #ff3366; }

    /* 9. TABS (ONGLETS) */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        color: #666;
    }
    .stTabs [aria-selected="true"] {
        color: var(--neon-cyan) !important;
        border-bottom-color: var(--neon-cyan) !important;
    }

    /* 10. METRICS */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: var(--neon-cyan) !important;
        font-size: 2.2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #888 !important;
    }

    /* 11. DATAFRAME */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.1);
        background-color: rgba(0,0,0,0.2);
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🏗️ FONCTIONS
# =========================================================
def get_data():
    conn = sqlite3.connect("leboncoin.db")
    try:
        df = pd.read_sql_query("SELECT * FROM annonces ORDER BY date_ajout DESC", conn)
        conn.close()
        return df
    except:
        conn.close()
        return pd.DataFrame()

# =========================================================
# 🖥️ HEADER ANIMÉ
# =========================================================
# On injecte le titre avec la classe CSS personnalisée
st.markdown("""
    <div class="title-anim">LBC HUNTER</div>
""", unsafe_allow_html=True)

# =========================================================
# 📑 SYSTEME D'ONGLETS
# =========================================================
tab_run, tab_data = st.tabs(["[>_] TERMINAL", "[|||] DATABASE"])

# ---------------------------------------------------------
# ONGLET 1 : LE TERMINAL (SCRAPER)
# ---------------------------------------------------------
with tab_run:
    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
    st.markdown("### 📡 INITIALISATION RECHERCHE")
    
    col_in, col_go = st.columns([4, 1])
    with col_in:
        query = st.text_input("TARGET_QUERY", placeholder="Ex: RTX 4070, Macbook M1...", label_visibility="collapsed")
    with col_go:
        start_btn = st.button("EXECUTE", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Console
    console_placeholder = st.empty()
    
    if start_btn:
        if not query:
            st.error(">> ERR: MISSING_ARGUMENT")
        else:
            logs = []
            console_placeholder.markdown(f"""
                <div class='console-box'>
                    <div class='log-line'>> SYSTEM READY.</div>
                    <div class='log-line'>> TARGET: <span style='color:white'>{query}</span></div>
                    <div class='log-line'>> LAUNCHING PROTOCOL...</div>
                </div>
            """, unsafe_allow_html=True)
            
            try:
                process = subprocess.Popen(
                    [sys.executable, "scraper.py", query],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    bufsize=1
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        # Style conditionnel pour les logs
                        css_class = "log-line"
                        if "Trouvé" in line or "annonces" in line: css_class = "log-line log-success"
                        if "Erreur" in line: css_class = "log-line log-error"
                        
                        logs.append(f"<div class='{css_class}'>> {line}</div>")
                        if len(logs) > 12: logs.pop(0)
                        
                        log_html = "".join(logs)
                        console_placeholder.markdown(f"<div class='console-box'>{log_html}</div>", unsafe_allow_html=True)
                
                if process.poll() == 0:
                    st.toast("✅ SCRAPING TERMINÉ AVEC SUCCÈS", icon="💾")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(">> FATAL ERROR DETECTED")

            except Exception as e:
                st.error(f">> SYSTEM EXCEPTION: {e}")

    elif not start_btn:
        console_placeholder.markdown("""
            <div class='console-box' style='display:flex; align-items:center; justify-content:center; color:#333;'>
                // WAITING FOR USER INPUT //
            </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# ONGLET 2 : LA DATA (DASHBOARD)
# ---------------------------------------------------------
with tab_data:
    df = get_data()
    
    if df.empty:
        st.info("NO DATA FOUND. PLEASE EXECUTE SCRAPER.")
    else:
        # KPI ROW
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("TOTAL ITEMS", len(df))
        avg = int(df['prix'].mean()) if not df.empty else 0
        k2.metric("AVG PRICE", f"{avg} €")
        min_p = int(df['prix'].min()) if not df.empty else 0
        k3.metric("BEST PRICE", f"{min_p} €")
        neuf = len(df[df['etat'].str.contains("Neuf|Scellé", case=False, na=False)])
        k4.metric("NEW ITEMS", neuf)
        st.markdown("</div>", unsafe_allow_html=True)

        # MAIN LAYOUT
        col_filters, col_charts = st.columns([1, 3])
        
        with col_filters:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("#### /// FILTERS")
            
            p_min, p_max = int(df['prix'].min()), int(df['prix'].max())
            if p_min == p_max: p_max += 100
            price_range = st.slider("BUDGET", p_min, p_max, (p_min, p_max))
            
            gpus = [x for x in df['gpu'].unique() if x != "Non spécifié"]
            gpu_select = st.multiselect("GPU MODEL", gpus)
            
            rams = sorted([x for x in df['ram'].unique() if pd.notnull(x)])
            ram_select = st.multiselect("RAM SIZE", rams)
            st.markdown("</div>", unsafe_allow_html=True)

        # Application filtres
        mask = (df['prix'] >= price_range[0]) & (df['prix'] <= price_range[1])
        if gpu_select: mask = mask & df['gpu'].isin(gpu_select)
        if ram_select: mask = mask & df['ram'].isin(ram_select)
        df_filtered = df[mask]

        with col_charts:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            tab_c1, tab_c2 = st.tabs(["DISTRIBUTION", "ETAT"])
            with tab_c1:
                st.bar_chart(df_filtered.set_index('titre')['prix'], color="#00F3FF")
            with tab_c2:
                st.bar_chart(df_filtered['etat'].value_counts(), color="#BC13FE")
            st.markdown("</div>", unsafe_allow_html=True)

        # TABLEAU
        st.markdown("### /// DATA_STREAM")
        
        col_config = {
            "url": st.column_config.LinkColumn("LINK", display_text="OPEN_LINK"),
            "prix": st.column_config.NumberColumn("PRIX", format="%d €"),
            "ssd": st.column_config.NumberColumn("SSD", format="%d Go"),
            "ram": st.column_config.NumberColumn("RAM", format="%d Go"),
            "description": st.column_config.TextColumn("INFO", width="medium")
        }
        
        cols = ['titre', 'prix', 'etat', 'gpu', 'ram', 'ssd', 'ville', 'url']
        cols_ok = [c for c in cols if c in df_filtered.columns]

        st.dataframe(
            df_filtered[cols_ok],
            column_config=col_config,
            use_container_width=True,
            hide_index=True
        )
