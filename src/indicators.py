"""
Calcul des KPI de mobilité et de sécurité routière.
- kpi_national.csv  : 1 ligne par année (1990-2022)
- kpi_regional.csv  : 1 ligne par région (snapshot 2022)
- kpi_reseau_etat.csv : national par état du réseau
"""
import pandas as pd
import numpy as np
from pathlib import Path
from shapely import wkt as shapely_wkt
from pyproj import Transformer
import shapely

from src.config import PROCESSED_DIR, SOURCE_FILES, GEO_REFERENCE_PATH
from src.io_utils import read_csv, write_csv


# Projection métrique pour le Togo (UTM zone 31N)

# ---------- Helpers ----------
def _read_processed(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / name, encoding="utf-8")


def _parse_geom(s):
    """Parse WKT en géométrie shapely, None si invalide."""
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        import shapely.wkt as swkt
        return swkt.loads(s)
    except Exception:
        return None

from src.route_utils import compute_route_lengths


# ============================================================
# KPI NATIONAUX
# ============================================================
def build_kpi_national() -> pd.DataFrame:
    # Population nationale (Banque Mondiale)
    pop = read_csv(SOURCE_FILES["pop_national"])
    pop.columns = [c.strip().lower() for c in pop.columns]
    pop["annee"] = pop["annee"].astype(int)
    # Limiter à la période d'analyse
    pop = pop[(pop["annee"] >= 1990) & (pop["annee"] <= 2022)].copy()

    # Immatriculations
    immat = _read_processed("immatriculations_wide.csv")
    immat = immat.rename(columns={
        "2 R et Assimilées": "immat_motos",
        "Autocars/Autobus": "immat_autocars",
        "Camionnettes": "immat_camionnettes",
        "Camions": "immat_camions",
        "Semi-remorques": "immat_semi_remorques",
        "Tracteurs": "immat_tracteurs",
        "Voitures": "immat_voitures",
        "total": "immat_total",
        "variation_annuelle": "immat_variation",
    })
    immat["immat_poids_lourds"] = (
        immat.get("immat_camions", 0)
        + immat.get("immat_semi_remorques", 0)
        + immat.get("immat_tracteurs", 0)
    )

    # Permis
    permis = _read_processed("permis_wide.csv")
    permis = permis.rename(columns={
        "Moto (A)": "permis_A",
        "Voiture légère (B)": "permis_B",
        "Poids lourd (C)": "permis_C",
        "Transport en commun (D)": "permis_D",
        "Semi-remorque (E)": "permis_E",
        "Voiture spéciale (F)": "permis_F",
        "total": "permis_total",
    })

    # Transports : on retire permis_total (déjà dans la table permis)
    transports = _read_processed("transports_clean_wide.csv")
    transports = transports.drop(columns=["permis_total"], errors="ignore")

    # Fusion
    df = pop.merge(immat, on="annee", how="left")
    df = df.merge(permis, on="annee", how="left")
    df = df.merge(transports, on="annee", how="left")
    df = df.sort_values("annee").reset_index(drop=True)

    # --- KPI dérivés ---
    df["immat_pour_1000_hab"] = df["immat_total"] / df["population"] * 1000
    df["part_motos_pct"] = df["immat_motos"] / df["immat_total"] * 100
    df["ratio_permis_immat"] = df["permis_total"] / df["immat_total"]

    df["accidents_pour_100k_hab"] = df["nb_accidents"] / df["population"] * 100_000
    df["morts_pour_100k_hab"] = df["nb_morts"] / df["population"] * 100_000
    df["blesses_pour_100k_hab"] = df["nb_blesses"] / df["population"] * 100_000
    df["morts_pour_10k_immat"] = df["nb_morts"] / df["immat_total"] * 10_000
    df["taux_mortalite_pct"] = df["nb_morts"] / df["nb_accidents"] * 100
    df["gravite_blesses"] = df["nb_blesses"] / df["nb_accidents"]

    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].round(3)

    write_csv(df, PROCESSED_DIR / "kpi_national.csv")
    return df


# ============================================================
# KPI RÉGIONAUX (snapshot 2022)
# ============================================================
def build_kpi_regional() -> pd.DataFrame:
    ref = pd.read_csv(GEO_REFERENCE_PATH, encoding="utf-8")

    # Population par région
    pop_region = ref.groupby("region", as_index=False)["population"].sum()

    # Auto-écoles par région
    auto = _read_processed("auto_ecoles_enriched.csv")
    ae_region = auto.groupby("region_canon").size().reset_index(name="nb_auto_ecoles")
    ae_region = ae_region.rename(columns={"region_canon": "region"})

    # Routes classées par région — avec longueur totale
    routes = _read_processed("routes_classees_enriched.csv")
    routes = compute_route_lengths(routes)
    routes_region = routes.groupby("region_canon").agg(
        nb_troncons=("fid", "count"),
        longueur_routes_km=("longueur_km", "sum"),
    ).reset_index().rename(columns={"region_canon": "region"})

    # Fusion
    df = pop_region.merge(ae_region, on="region", how="left")
    df = df.merge(routes_region, on="region", how="left")
    df = df.fillna({"nb_auto_ecoles": 0, "nb_troncons": 0, "longueur_routes_km": 0})

    # KPI dérivés
    df["auto_ecoles_pour_100k_hab"] = df["nb_auto_ecoles"] / df["population"] * 100_000
    df["km_routes_pour_1000_hab"] = df["longueur_routes_km"] / df["population"] * 1000
    df["km_par_troncon"] = np.where(
        df["nb_troncons"] > 0,
        df["longueur_routes_km"] / df["nb_troncons"],
        0,
    )

    df = df.sort_values("population", ascending=False).reset_index(drop=True)
    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].round(3)

    write_csv(df, PROCESSED_DIR / "kpi_regional.csv")
    return df


# ============================================================
# KPI RÉSEAU PAR ÉTAT
# ============================================================
def build_kpi_reseau_etat() -> pd.DataFrame:
    reseau = _read_processed("reseau_routier_clean.csv")

    # Agrégation nationale par catégorie / revêtement / état
    agg = reseau.groupby(
        ["categorie", "revetement", "etat"], as_index=False
    )["valeur"].sum()

    # Total par catégorie/revêtement
    total = reseau.groupby(
            ["categorie", "revetement"], as_index=False
     )["valeur"].sum().rename(columns={"valeur": "longueur_totale_km"})

    agg = agg.merge(total, on=["categorie", "revetement"])
    agg["part_pct"] = (agg["valeur"] / agg["longueur_totale_km"] * 100).round(2)
    agg = agg.rename(columns={"valeur": "longueur_km"})

    write_csv(agg, PROCESSED_DIR / "kpi_reseau_etat.csv")
    return agg


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("CALCUL DES KPI")
    print("=" * 60)

    nat = build_kpi_national()
    print(f"\n✅ kpi_national : {len(nat)} années")
    cols_show = ["annee", "immat_total", "immat_motos", "nb_accidents",
                 "nb_morts", "morts_pour_100k_hab", "part_motos_pct"]
    cols_show = [c for c in cols_show if c in nat.columns]
    print("\nExtrait 2018-2022 :")
    print(nat[nat["annee"] >= 2018][cols_show].to_string(index=False))

    reg = build_kpi_regional()
    print(f"\n✅ kpi_regional : {len(reg)} régions")
    print("\nClassement par population :")
    print(reg[["region", "population", "nb_auto_ecoles",
               "auto_ecoles_pour_100k_hab", "longueur_routes_km",
               "km_routes_pour_1000_hab"]].to_string(index=False))

    etat = build_kpi_reseau_etat()
    print(f"\n✅ kpi_reseau_etat : {len(etat)} combinaisons")
    print(etat.to_string(index=False))