import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pathlib import Path
import streamlit as st

# Chemins définis avant set_page_config
BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="Dashboard Projet ATER-MOB I",
    page_icon=str(BASE_DIR / "img" / "logo-lion.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session state : source de vérité ----------
if "page" not in st.session_state:
    st.session_state.page = st.query_params.get("p", "accueil")
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = st.query_params.get("sb", "open")
if "theme" not in st.session_state:
    st.session_state.theme = st.query_params.get("th", "light")

page = st.session_state.page
sidebar_state = st.session_state.sidebar_state
theme = st.session_state.theme

# ---------- Registre des pages ----------
PAGES = {
    "accueil": {"label": "Accueil", "icon": "home",
                "description": "Vue d'ensemble de la mobilité et de la sécurité routière au Togo."},
    "mobilite": {"label": "Mobilité", "icon": "directions_car",
                 "description": "Évolution des immatriculations et des permis de conduire délivrés par catégorie."},
    "securite": {"label": "Sécurité routière", "icon": "warning",
                 "description": "Analyse des accidents, blessés et morts rapportés à la population et au parc de véhicules."},
    "infrastructures": {"label": "Infrastructures & Réseau", "icon": "add_road",
                        "description": "État du réseau routier national, routes classées et cartographie des tronçons."},
    "auto_ecoles": {"label": "Auto-écoles", "icon": "school",
                    "description": "Répartition et densité des auto-écoles par région et préfecture."},
    "population": {"label": "Population & territoire", "icon": "groups",
                   "description": "Données démographiques (RGPH5) pour normaliser les indicateurs par région."},
    "recommandations": {"label": "Recommandations", "icon": "lightbulb",
                        "description": "Synthèse des analyses et pistes stratégiques pour une mobilité plus sûre."},
}

if page not in PAGES:
    page = "accueil"
    st.session_state.page = page

# ---------- Sync URL (partageable) ----------
st.query_params.update({"p": page, "sb": sidebar_state, "th": theme})

# ---------- CSS global ----------
st.markdown(
    f"<style>{(BASE_DIR / 'styles' / 'style.css').read_text()}</style>",
    unsafe_allow_html=True,
)

# ---------- CSS sidebar mini ----------
if sidebar_state == "mini":
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            width: 72px !important; min-width: 72px !important; max-width: 72px !important;
        }
        [data-testid="stSidebar"] .sidebar-logo img {
            max-width: 42px !important; margin: 0 auto !important; display: block;
        }
        [data-testid="stSidebar"] .stButton > button p { display: none; }
        [data-testid="stSidebar"] .stButton > button {
            justify-content: center !important;
            padding: 12px 6px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------- CSS thème sombre ----------
if theme == "dark":
    st.markdown("""
        <style>
        .stApp, [data-testid="stAppViewContainer"] { background-color: #0e1117; color: #f0f6fc; }
        [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
        [data-testid="stSidebar"] .stButton > button { color: #c9d1d9 !important; }
        [data-testid="stSidebar"] .stButton > button:hover { background-color: #21262d !important; }
        [data-testid="stSidebar"] .stButton > button[kind="primary"],
        [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
            background-color: rgba(31,111,235,0.15) !important;
            color: #58a6ff !important;
        }
        .sidebar-logo { border-bottom-color: #30363d; }
        .topbar-title { color: #f0f6fc; }
        .topbar-icon-btn { color: #c9d1d9; }
        .topbar-icon-btn:hover { background-color: #21262d; }
        .page-header { background: linear-gradient(135deg, #161b22 0%, #1c2630 100%); border-color: #30363d; }
        .page-header-title { color: #f0f6fc; }
        .page-header-desc { color: #8b949e; }
        .content-placeholder { background-color: #161b22; border-color: #30363d; color: #8b949e; }
        .footer-hr { border-top-color: #30363d; }
        .footer-text { color: #c9d1d9; }
        .footer-text strong { color: #f0f6fc; }
        </style>
    """, unsafe_allow_html=True)

# ---------- Imports ----------
from components.sidebar import render_sidebar
from components.topbar import render_topbar
from components.page_header import render_page_header
from components.footer import render_footer

from views import (
    accueil, mobilite, securite, infrastructures,
    auto_ecoles, population, recommandations,
)

VIEW_RENDERERS = {
    "accueil": accueil.render,
    "mobilite": mobilite.render,
    "securite": securite.render,
    "infrastructures": infrastructures.render,
    "auto_ecoles": auto_ecoles.render,
    "population": population.render,
    "recommandations": recommandations.render,
}

# ---------- Rendu ----------
render_sidebar(PAGES, page)
render_topbar(page)
render_page_header(PAGES[page]["label"], PAGES[page]["description"])
VIEW_RENDERERS[page]()
render_footer()
