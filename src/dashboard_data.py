"""
Couche d'accès aux données pour le dashboard Streamlit.
"""
import re
from pathlib import Path
import pandas as pd
import streamlit as st
from src.config import SOURCE_FILES

from src.config import PROCESSED_DIR, GEO_REFERENCE_PATH


_WKT_POINT_RE = re.compile(r"POINT\s*\(\s*([-0-9.]+)\s+([-0-9.]+)\s*\)")


def _parse_wkt_point(s):
    if not isinstance(s, str):
        return (None, None)
    m = _WKT_POINT_RE.search(s)
    if not m:
        return (None, None)
    try:
        return (float(m.group(1)), float(m.group(2)))
    except ValueError:
        return (None, None)
import json
from src.config import GEOJSON_FILES, GADM_TO_RGPH5_REGION


@st.cache_data(show_spinner=False)
def load_regions_geojson():
    """Charge le GeoJSON régions et ajoute un attribut region_canon."""
    with open(GEOJSON_FILES["regions"], encoding="utf-8") as f:
        gj = json.load(f)
    for feat in gj["features"]:
        name = feat["properties"].get("NAME_1", "")
        canon = GADM_TO_RGPH5_REGION.get(name.strip().lower(), name.strip().lower())
        feat["properties"]["region_canon"] = canon
    return gj


@st.cache_data(show_spinner=False)
def load_auto_ecoles() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "auto_ecoles_enriched.csv", encoding="utf-8")
    coords = df["geometry"].apply(_parse_wkt_point)
    df["lon"] = [c[0] for c in coords]
    df["lat"] = [c[1] for c in coords]
    return df


@st.cache_data(show_spinner=False)
def load_geo_reference() -> pd.DataFrame:
    return pd.read_csv(GEO_REFERENCE_PATH, encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_kpi_regional() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "kpi_regional.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_kpi_national() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "kpi_national.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_kpi_reseau_etat() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "kpi_reseau_etat.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_routes_classees() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "routes_classees_enriched.csv", encoding="utf-8")

@st.cache_data(show_spinner=False)
def load_reseau_routier():
    return pd.read_csv(PROCESSED_DIR / "reseau_routier_clean.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_routes_classees():
    df = pd.read_csv(PROCESSED_DIR / "routes_classees_enriched.csv", encoding="utf-8")
    # calcul longueur + extraction lat/lon pour centrage
    return df

# ---------- Helpers ----------
def filter_auto_ecoles(df, region=None, prefecture=None, commune=None):
    d = df.copy()
    if region and region != "Toutes":
        d = d[d["region_canon"] == region]
    if prefecture and prefecture != "Toutes":
        d = d[d["prefecture_canon"] == prefecture]
    if commune and commune != "Toutes":
        d = d[d["commune_canon"] == commune]
    return d


def get_population_by_level(ref, level):
    if level == "region":
        return ref.groupby("region", as_index=False)["population"].sum()
    if level == "prefecture":
        return ref.groupby(["region", "prefecture"], as_index=False)["population"].sum()
    if level == "commune":
        return ref.groupby(["region", "prefecture", "commune"], as_index=False)["population"].sum()
    raise ValueError(level)


def count_by_level(df, level):
    col_map = {"region": "region_canon", "prefecture": "prefecture_canon", "commune": "commune_canon"}
    col = col_map[level]
    counts = df.groupby(col).size().reset_index(name="nb")
    return counts.rename(columns={col: level})

# ============================================================
# RESEAU ROUTIER + ROUTES CLASSEES
# ============================================================
@st.cache_data(show_spinner=False)
def load_reseau_routier() -> pd.DataFrame:
    """Réseau routier 2020 — agrégé par tronçon/état/catégorie/revêtement."""
    return pd.read_csv(PROCESSED_DIR / "reseau_routier_clean.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_routes_classees() -> pd.DataFrame:
    """Routes classées enrichies + longueur calculée."""
    from src.route_utils import compute_route_lengths
    df = pd.read_csv(PROCESSED_DIR / "routes_classees_enriched.csv", encoding="utf-8")
    df = compute_route_lengths(df, geom_col="geometry")
    return df

@st.cache_data(show_spinner=False)
def load_areas_regions():
    return pd.read_csv(PROCESSED_DIR / "areas_regions.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_areas_prefectures():
    return pd.read_csv(PROCESSED_DIR / "areas_prefectures.csv", encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_prefectures_geojson():
    """GeoJSON des préfectures avec attributs canoniques."""
    import json
    with open(GEOJSON_FILES["prefectures"], encoding="utf-8") as f:
        gj = json.load(f)
    for feat in gj["features"]:
        # Normaliser
        import unicodedata, re
        def norm(s):
            if not s: return ""
            s = str(s).strip().lower().replace("-", " ")
            s = "".join(c for c in unicodedata.normalize("NFKD", s)
                        if not unicodedata.combining(c))
            return re.sub(r"\s+", " ", s)
        r = norm(feat["properties"].get("NAME_1", ""))
        p = norm(feat["properties"].get("NAME_2", ""))
        feat["properties"]["region_canon"] = "centrale" if r == "centre" else r
        feat["properties"]["prefecture_canon"] = p
    return gj

@st.cache_data(show_spinner=False)
def load_pop_national() -> pd.DataFrame:
    """Population nationale Banque Mondiale (1960-2025)."""
    df = pd.read_csv(SOURCE_FILES["pop_national"], encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]
    df["annee"] = df["annee"].astype(int)
    return df.sort_values("annee").reset_index(drop=True)