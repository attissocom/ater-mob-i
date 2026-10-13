"""
Utilitaires d'entrée/sortie : lecture CSV/GeoJSON, écriture CSV,
gestion du fichier d'overrides manuels.
"""
import json
from pathlib import Path
import pandas as pd

from src.config import ENCODING, OVERRIDES_PATH


# ---------- Lecture ----------
def read_csv(path, **kwargs) -> pd.DataFrame:
    """Lit un CSV en UTF-8, avec index par défaut."""
    return pd.read_csv(path, encoding=ENCODING, **kwargs)


def read_geojson(path) -> dict:
    """Lit un GeoJSON et renvoie le dict brut."""
    with open(path, "r", encoding=ENCODING) as f:
        return json.load(f)


def read_geojson_gdf(path):
    """Lit un GeoJSON en GeoDataFrame (geopandas)."""
    import geopandas as gpd
    return gpd.read_file(path)


# ---------- Écriture ----------
def write_csv(df: pd.DataFrame, path, **kwargs) -> None:
    """Écrit un CSV UTF-8 en créant le dossier parent si besoin."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding=ENCODING, **kwargs)


# ---------- Overrides manuels ----------
OVERRIDE_COLUMNS = [
    "dataset_source",
    "niveau",              # region | prefecture | commune | canton
    "name_normalized",     # clé de matching normalisée
    "name_canonical",      # valeur cible (nom canonique)
    "region",              # région cible (canonique)
    "prefecture",          # préfecture cible
    "commune",             # commune cible
    "canton",              # canton cible
    "commentaire",
]


def ensure_overrides_file() -> None:
    """Crée un overrides vide s'il n'existe pas encore."""
    if not OVERRIDES_PATH.exists():
        pd.DataFrame(columns=OVERRIDE_COLUMNS).to_csv(
            OVERRIDES_PATH, index=False, encoding=ENCODING
        )


def load_overrides() -> pd.DataFrame:
    """Charge les overrides manuels (vide par défaut)."""
    ensure_overrides_file()
    df = pd.read_csv(OVERRIDES_PATH, encoding=ENCODING, dtype=str).fillna("")
    return df