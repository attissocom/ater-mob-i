"""
Applique le crosswalk géographique aux datasets sources.
Enrichit chaque ligne avec les clés canoniques RGPH5.
Sauvegarde le résultat dans data/processed/.
"""
import pandas as pd
from pathlib import Path

from src.config import SOURCE_FILES, CROSSWALK_PATH, PROCESSED_DIR
from src.io_utils import read_csv, write_csv
from src.geo_normalize import normalize_series


def _build_lookups(cw_src: pd.DataFrame):
    """Construit les dictionnaires de mapping par niveau."""
    reg = cw_src[cw_src["niveau"] == "region"]
    pref = cw_src[cw_src["niveau"] == "prefecture"]
    com = cw_src[cw_src["niveau"] == "commune"]
    can = cw_src[cw_src["niveau"] == "canton"]

    region_lookup = reg.set_index("name_normalized")["name_canonical"].to_dict()
    pref_lookup = pref.set_index(["region", "name_normalized"])["name_canonical"].to_dict()
    com_lookup = com.set_index(["region", "prefecture", "name_normalized"])["name_canonical"].to_dict()
    can_lookup = can.set_index(["region", "prefecture", "commune", "name_normalized"])["name_canonical"].to_dict()

    return region_lookup, pref_lookup, com_lookup, can_lookup


def apply_crosswalk(df: pd.DataFrame, source_name: str,
                    col_region: str, col_prefecture: str,
                    col_commune: str, col_canton: str) -> pd.DataFrame:
    """
    Enrichit df avec :
      - region_norm / region_canon
      - prefecture_norm / prefecture_canon
      - commune_norm / commune_canon
      - canton_norm / canton_canon
    """
    cw = pd.read_csv(CROSSWALK_PATH, encoding="utf-8")
    cw_src = cw[cw["dataset_source"] == source_name]
    region_lookup, pref_lookup, com_lookup, can_lookup = _build_lookups(cw_src)

    df = df.copy()

    # Normalisation des colonnes source
    df["region_norm"]     = normalize_series(df[col_region])
    df["prefecture_norm"] = normalize_series(df[col_prefecture])
    df["commune_norm"]    = normalize_series(df[col_commune])
    df["canton_norm"]     = normalize_series(df[col_canton])

    # Application hiérarchique
    df["region_canon"] = df["region_norm"].map(region_lookup)

    df["prefecture_canon"] = [
        pref_lookup.get((r, p))
        for r, p in zip(df["region_canon"], df["prefecture_norm"])
    ]

    df["commune_canon"] = [
        com_lookup.get((r, p, c))
        for r, p, c in zip(df["region_canon"], df["prefecture_canon"], df["commune_norm"])
    ]

    df["canton_canon"] = [
        can_lookup.get((r, p, c, k))
        for r, p, c, k in zip(df["region_canon"], df["prefecture_canon"],
                              df["commune_canon"], df["canton_norm"])
    ]

    return df


def process_routes_classees() -> pd.DataFrame:
    df = read_csv(SOURCE_FILES["routes_classees"])
    df.columns = [c.strip().lower() for c in df.columns]
    enriched = apply_crosswalk(
        df, "routes_classees",
        col_region="region_nom_bdd",
        col_prefecture="prefecture_nom_bdd",
        col_commune="commune_nom_bdd",
        col_canton="canton_nom_bdd",
    )
    write_csv(enriched, PROCESSED_DIR / "routes_classees_enriched.csv")
    return enriched


def process_auto_ecoles() -> pd.DataFrame:
    df = read_csv(SOURCE_FILES["entreprises_auto_ecoles"])
    df.columns = [c.strip().lower() for c in df.columns]
    enriched = apply_crosswalk(
        df, "auto_ecoles",
        col_region="region_nom_bdd",
        col_prefecture="prefecture_nom_bdd",
        col_commune="commune_nom_bdd",
        col_canton="canton_nom_bdd",
    )
    enriched = clean_aggregation(enriched)
    write_csv(enriched, PROCESSED_DIR / "auto_ecoles_enriched.csv")
    return enriched

def clean_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie la colonne agregation :
    - 'Antenne agréée' → 'Agréée'
    - Exclut les lignes 'Néant' (2 lignes)
    """
    if "agregation" not in df.columns:
        return df
    df = df.copy()
    df["agregation"] = df["agregation"].astype(str).str.strip()
    # Fusion Antenne agréée → Agréée
    df["agregation"] = df["agregation"].replace({"Antenne agréée": "Agréée"})
    # Exclusion Néant
    df = df[df["agregation"] != "Néant"].reset_index(drop=True)
    return df


if __name__ == "__main__":
    routes = process_routes_classees()
    auto = process_auto_ecoles()

    print(f"✅ routes_classees_enriched : {len(routes)} lignes")
    print(f"   - region_canon non nul     : {routes['region_canon'].notna().sum()}")
    print(f"   - prefecture_canon non nul : {routes['prefecture_canon'].notna().sum()}")
    print(f"   - commune_canon non nul    : {routes['commune_canon'].notna().sum()}")
    print(f"   - canton_canon non nul     : {routes['canton_canon'].notna().sum()}")

    print(f"\n✅ auto_ecoles_enriched : {len(auto)} lignes")
    print(f"   - region_canon non nul     : {auto['region_canon'].notna().sum()}")
    print(f"   - prefecture_canon non nul : {auto['prefecture_canon'].notna().sum()}")
    print(f"   - commune_canon non nul    : {auto['commune_canon'].notna().sum()}")
    print(f"   - canton_canon non nul     : {auto['canton_canon'].notna().sum()}")

    print("\n--- Répartition région_canon (routes) ---")
    print(routes["region_canon"].value_counts(dropna=False).to_string())

    print("\n--- Répartition région_canon (auto_ecoles) ---")
    print(auto["region_canon"].value_counts(dropna=False).to_string())

    print("\n--- Aperçu routes enrichies ---")
    print(routes[["route_nom", "region_canon", "prefecture_canon",
                  "commune_canon", "canton_canon"]].head(10).to_string(index=False))