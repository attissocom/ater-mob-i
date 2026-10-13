"""
Construit le référentiel géographique canonique (geo_reference.csv)
à partir de pop_rgph5_tg, avec la règle Grand Lomé → Maritime.
"""
import pandas as pd
from src.config import SOURCE_FILES, GEO_REFERENCE_PATH
from src.io_utils import read_csv, write_csv
from src.geo_normalize import normalize_series, apply_grand_lome_rule


def build_reference() -> pd.DataFrame:
    pop = read_csv(SOURCE_FILES["pop_rgph5_tg"])

    # Région : appliquer Grand Lomé → Maritime, puis normaliser
    pop["region"] = pop["region_nom_bdd"].map(apply_grand_lome_rule)
    pop["region"] = normalize_series(pop["region"])

    pop["prefecture"] = normalize_series(pop["prefecture_nom_bdd"])
    pop["commune"]    = normalize_series(pop["commune_nom_bdd"])
    pop["canton"]     = normalize_series(pop["canton_nom_bdd"])

    ref = (
        pop.groupby(["region", "prefecture", "commune", "canton"], dropna=False)["population"]
        .sum()
        .reset_index()
    )
    ref = ref.sort_values(["region", "prefecture", "commune", "canton"]).reset_index(drop=True)
    write_csv(ref, GEO_REFERENCE_PATH)
    return ref


if __name__ == "__main__":
    ref = build_reference()
    print(f"Référentiel généré : {len(ref)} lignes")
    print(f"Colonnes : {list(ref.columns)}")
    print("\nRégions :", sorted(ref['region'].dropna().unique()))
    print(f"Préfectures uniques : {ref['prefecture'].nunique()}")
    print(f"Communes uniques    : {ref['commune'].nunique()}")