"""
Configuration centrale du projet ATER-MOB I.
Chemins, seuils, règles métier et fichiers sources.
"""
from pathlib import Path

# ---------- Arborescence ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
MAPPINGS_DIR = DATA_DIR / "mappings"
PROCESSED_DIR = DATA_DIR / "processed"

for _d in (MAPPINGS_DIR, PROCESSED_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------- Fichiers sources ----------
SOURCE_FILES = {
    "transports_terrestres":  RAW_DIR / "transports_terrestres.csv",
    "routes_classees":        RAW_DIR / "routes_classees.csv",
    "reseau_routier":         RAW_DIR / "reseau_routier.csv",
    "pop_rgph5_tg":           RAW_DIR / "pop_rgph5_tg.csv",
    "permis_conduire":        RAW_DIR / "permis_conduire.csv",
    "immatriculations_1":     RAW_DIR / "immatriculations_1.csv",
    "immatriculations_2":     RAW_DIR / "immatriculations_2.csv",
    "entreprises_auto_ecoles": RAW_DIR / "entreprises_auto_ecoles.csv",
    "pop_national":            RAW_DIR / "pop_tg_1960_2025.csv",
}

GEOJSON_FILES = {
    "regions":     RAW_DIR / "regions.geojson",
    "prefectures": RAW_DIR / "prefectures.geojson",
}

# ---------- Fichiers générés ----------
CROSSWALK_PATH       = MAPPINGS_DIR  / "geo_crosswalk.csv"
OVERRIDES_PATH       = MAPPINGS_DIR  / "geo_crosswalk_overrides.csv"
GEO_REFERENCE_PATH   = PROCESSED_DIR / "geo_reference.csv"

# ---------- Paramètres de matching ----------
FUZZY_THRESHOLD = 85           # 0-100 : en-dessous → needs_review=True
ENCODING = "utf-8"

# ---------- Règle métier : découpage régional (5 régions) ----------
CANONICAL_REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]

# Grand Lomé (créé en 2018) → rattaché à Maritime
GRAND_LOME_ALIASES = {"grand lome", "grand-lome", "grandlome", "golfe"}
GRAND_LOME_TARGET  = "maritime"

# Correspondance GADM (GeoJSON) → RGPH5 (référentiel canonique)
GADM_TO_RGPH5_REGION = {
    "centre":   "centrale",
    "kara":     "kara",
    "maritime": "maritime",
    "plateaux": "plateaux",
    "savanes":  "savanes",
}

# Noms de colonnes GADM dans les GeoJSON
GEOJSON_REGION_COL  = "NAME_1"   # région (regions.geojson)
GEOJSON_PREF_REGION = "NAME_1"   # région parente (prefectures.geojson)
GEOJSON_PREF_NAME   = "NAME_2"   # préfecture (prefectures.geojson)

# ---------- Alternatives (fallback si GeoJSON incomplet) ----------
# GADM  : https://gadm.org/download_country.html (Togo)
# HDX   : https://data.humdata.org/dataset/cod-ab-tgo
# OSM   : via osmnx / osm-boundaries.com