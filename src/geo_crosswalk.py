"""
Crosswalk géographique complet :
- matching hiérarchique région → préfecture → commune → canton
- rapidefuzz restreint à chaque niveau par le parent déjà mappé
- surcharge par overrides manuels si présents
- sortie : data/mappings/geo_crosswalk.csv
"""
import pandas as pd
from rapidfuzz import process, fuzz

from src.config import SOURCE_FILES, CROSSWALK_PATH, FUZZY_THRESHOLD
from src.io_utils import read_csv, write_csv, load_overrides
from src.geo_normalize import normalize_series, apply_grand_lome_rule
from src.build_reference import build_reference


CROSSWALK_COLUMNS = [
    "dataset_source", "niveau", "name_source", "name_normalized",
    "name_canonical", "region", "prefecture", "commune", "canton",
    "score", "method", "needs_review",
]


def build_hierarchy(ref: pd.DataFrame):
    regions = sorted(ref["region"].dropna().unique())

    prefs_by_region = (
        ref.dropna(subset=["prefecture"])
        .groupby("region")["prefecture"]
        .apply(lambda s: sorted(s.unique()))
        .to_dict()
    )
    comms_by_pref = (
        ref.dropna(subset=["commune"])
        .groupby(["region", "prefecture"])["commune"]
        .apply(lambda s: sorted(s.unique()))
        .to_dict()
    )
    cants_by_comm = (
        ref.dropna(subset=["canton"])
        .groupby(["region", "prefecture", "commune"])["canton"]
        .apply(lambda s: sorted(s.unique()))
        .to_dict()
    )
    return regions, prefs_by_region, comms_by_pref, cants_by_comm


def _match(query: str, choices, threshold=FUZZY_THRESHOLD):
    if not query or not choices:
        return (None, 0, "none")
    result = process.extractOne(query, choices, scorer=fuzz.ratio)
    if result is None:
        return (None, 0, "none")
    match, score, _ = result
    if score >= threshold:
        method = "exact" if score == 100 else "fuzzy"
        return (match, int(score), method)
    return (None, int(score), "needs_review")


def _norm(val) -> str:
    if val is None or pd.isna(val):
        return ""
    return normalize_series(pd.Series([str(val)])).iloc[0]


def match_hierarchy(df: pd.DataFrame, source_name: str,
                    col_region: str, col_prefecture: str = None,
                    col_commune: str = None, col_canton: str = None) -> pd.DataFrame:
    """
    Matching hiérarchique d'un DataFrame source.
    Produit le crosswalk des 4 niveaux pour chaque combinaison unique observée.
    """
    ref = build_reference()
    regions, prefs_by_region, comms_by_pref, cants_by_comm = build_hierarchy(ref)

    # Colonnes optionnelles
    cols = [col_region, col_prefecture, col_commune, col_canton]
    cols = [c for c in cols if c and c in df.columns]

    unique = df[cols].drop_duplicates().reset_index(drop=True)

    rows = []
    for _, r in unique.iterrows():
        # --- Région ---
        raw_reg = r.get(col_region)
        norm_reg = _norm(raw_reg)
        norm_reg = apply_grand_lome_rule(norm_reg) or norm_reg
        reg_match, reg_score, reg_method = _match(norm_reg, regions)

        rows.append({
            "dataset_source": source_name, "niveau": "region",
            "name_source": raw_reg, "name_normalized": norm_reg,
            "name_canonical": reg_match, "region": reg_match,
            "prefecture": None, "commune": None, "canton": None,
            "score": reg_score, "method": reg_method,
            "needs_review": reg_method == "needs_review",
        })

        if not reg_match:
            continue

        # --- Préfecture (restreint à la région mappée) ---
        if col_prefecture:
            raw_pref = r.get(col_prefecture)
            norm_pref = _norm(raw_pref)
            choices = prefs_by_region.get(reg_match, [])
            pref_match, pref_score, pref_method = _match(norm_pref, choices)

            rows.append({
                "dataset_source": source_name, "niveau": "prefecture",
                "name_source": raw_pref, "name_normalized": norm_pref,
                "name_canonical": pref_match, "region": reg_match,
                "prefecture": pref_match, "commune": None, "canton": None,
                "score": pref_score, "method": pref_method,
                "needs_review": pref_method == "needs_review",
            })

            if not pref_match:
                continue

            # --- Commune (restreinte à la préfecture mappée) ---
            if col_commune:
                raw_com = r.get(col_commune)
                norm_com = _norm(raw_com)
                choices = comms_by_pref.get((reg_match, pref_match), [])
                com_match, com_score, com_method = _match(norm_com, choices)

                rows.append({
                    "dataset_source": source_name, "niveau": "commune",
                    "name_source": raw_com, "name_normalized": norm_com,
                    "name_canonical": com_match, "region": reg_match,
                    "prefecture": pref_match, "commune": com_match, "canton": None,
                    "score": com_score, "method": com_method,
                    "needs_review": com_method == "needs_review",
                })

                if not com_match:
                    continue

                # --- Canton (restreint à la commune mappée) ---
                if col_canton:
                    raw_can = r.get(col_canton)
                    norm_can = _norm(raw_can)
                    choices = cants_by_comm.get((reg_match, pref_match, com_match), [])
                    # Canton = affichage uniquement → seuil strict, jamais needs_review
                    can_match, can_score, _ = _match(norm_can, choices, threshold=90)
                    rows.append({
                        "dataset_source": source_name, "niveau": "canton",
                        "name_source": raw_can, "name_normalized": norm_can,
                        # Si pas de match fiable, on garde le nom normalisé pour affichage
                        "name_canonical": can_match if can_match else norm_can,
                        "region": reg_match, "prefecture": pref_match,
                        "commune": com_match, "canton": can_match,
                        "score": can_score,
                        "method": "exact" if can_score == 100 else
                                  ("fuzzy" if can_match else "display_only"),
                        "needs_review": False,
                 })

    return pd.DataFrame(rows, columns=CROSSWALK_COLUMNS)


def apply_overrides(cw: pd.DataFrame) -> pd.DataFrame:
    """Applique les overrides manuels (priorité haute)."""
    ov = load_overrides()
    if ov.empty:
        return cw

    cw = cw.copy()
    for _, o in ov.iterrows():
        mask = (
            (cw["dataset_source"] == o["dataset_source"]) &
            (cw["niveau"] == o["niveau"]) &
            (cw["name_normalized"] == o["name_normalized"])
        )
        cw.loc[mask, "name_canonical"] = o["name_canonical"]
        cw.loc[mask, "region"] = o["region"]
        cw.loc[mask, "prefecture"] = o["prefecture"]
        cw.loc[mask, "commune"] = o["commune"]
        cw.loc[mask, "canton"] = o["canton"]
        cw.loc[mask, "score"] = 100
        cw.loc[mask, "method"] = "override"
        cw.loc[mask, "needs_review"] = False
    return cw


def build_crosswalk() -> pd.DataFrame:
    """Point d'entrée : construit le crosswalk pour toutes les sources."""
    all_parts = []

    routes = read_csv(SOURCE_FILES["routes_classees"])
    routes.columns = [c.strip().lower() for c in routes.columns]
    all_parts.append(match_hierarchy(
        routes, "routes_classees",
        col_region="region_nom_bdd",
        col_prefecture="prefecture_nom_bdd",
        col_commune="commune_nom_bdd",
        col_canton="canton_nom_bdd",
    ))

    auto = read_csv(SOURCE_FILES["entreprises_auto_ecoles"])
    auto.columns = [c.strip().lower() for c in auto.columns]
    all_parts.append(match_hierarchy(
        auto, "auto_ecoles",
        col_region="region_nom_bdd",
        col_prefecture="prefecture_nom_bdd",
        col_commune="commune_nom_bdd",
        col_canton="canton_nom_bdd",
    ))

    cw = pd.concat(all_parts, ignore_index=True)
    cw = apply_overrides(cw)
    write_csv(cw, CROSSWALK_PATH)
    return cw


if __name__ == "__main__":
    cw = build_crosswalk()
    print(f"Crosswalk généré : {len(cw)} lignes")
    print(f"needs_review     : {int(cw['needs_review'].sum())}")
    print(f"\nPar niveau :")
    print(cw.groupby("niveau").size().to_string())
    print(f"\nMéthodes utilisées :")
    print(cw["method"].value_counts().to_string())
    print(f"\n--- Régions mappées ---")
    print(cw[cw["niveau"] == "region"][["dataset_source","name_source","name_normalized","name_canonical","score","method"]].to_string(index=False))
    print(f"\n--- Préfectures avec needs_review ---")
    nr = cw[(cw["niveau"] == "prefecture") & (cw["needs_review"])]
    print(nr[["dataset_source","name_source","name_normalized","score"]].head(20).to_string(index=False))