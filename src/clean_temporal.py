"""
Nettoyage des 4 datasets temporels :
- immatriculations_2 : parc/flux, types de véhicule
- permis_conduire   : catégories, interpolation 2013
- reseau_routier    : par tronçon et état, quarantaine VOIRIES EN TERRE
- transports_terrestres : version longue + version wide

Sortie : data/processed/*_clean.csv
"""
import pandas as pd
import numpy as np
from src.config import SOURCE_FILES, PROCESSED_DIR
from src.io_utils import read_csv, write_csv

# ⚙️ CONFIGURATION : à ajuster après le diagnostic parc/flux
IMMAT_SERIE = "flux"   # "parc" ou "flux" — sera documenté dans la colonne `serie`

# ---------- Helpers ----------
import unicodedata

def _strip_cols(df):
    def clean_col(c):
        c = str(c).strip().lower().replace("-", "_").replace(" ", "_")
        # Supprimer les accents (é → e, ç → c, è → e, etc.)
        c = "".join(
            ch for ch in unicodedata.normalize("NFKD", c)
            if not unicodedata.combining(ch)
        )
        return c
    df.columns = [clean_col(c) for c in df.columns]
    return df


def _clean_txt(df):
    for c in df.columns:
        if df[c].dtype == "object" or str(df[c].dtype).startswith("str"):
            df[c] = df[c].astype(str).str.strip()
    return df


# ============================================================
# 1) IMMATRICULATIONS_2
# ============================================================
def clean_immatriculations():
    df = read_csv(SOURCE_FILES["immatriculations_2"])
    df = _strip_cols(df)
    df = _clean_txt(df)

    # Renommage
    df = df.rename(columns={
        "types_de_vehicule": "type_vehicule",
        "unit": "unite",
        "date": "annee",
        "value": "valeur",
    })

    # Filtre au cas où des Total subsisteraient (sécurité)
    total_mask = df["type_vehicule"].str.lower().str.contains("total", na=False)
    if total_mask.any():
        quarantine = df[total_mask].copy()
        write_csv(quarantine, PROCESSED_DIR / "immatriculations_2_total_quarantine.csv")
        df = df[~total_mask].copy()

    # Cast
    df["annee"] = df["annee"].astype(int)
    df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

    # Colonne série (parc vs flux)
    df["serie"] = IMMAT_SERIE

    # Tri
    df = df[["annee", "type_vehicule", "valeur", "unite", "serie"]].sort_values(
        ["type_vehicule", "annee"]
    ).reset_index(drop=True)

    write_csv(df, PROCESSED_DIR / "immatriculations_clean.csv")
    return df


def build_immatriculations_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    """Version wide : 1 ligne par année, 1 colonne par type + total + variation annuelle."""
    wide = df_long.pivot_table(
        index="annee", columns="type_vehicule", values="valeur", aggfunc="sum"
    ).reset_index()
    wide.columns.name = None

    # Total annuel
    type_cols = [c for c in wide.columns if c != "annee"]
    wide["total"] = wide[type_cols].sum(axis=1)

    # Variation annuelle du total
    wide["variation_annuelle"] = wide["total"].diff()

    write_csv(wide, PROCESSED_DIR / "immatriculations_wide.csv")
    return wide


# ============================================================
# 2) PERMIS_CONDUIRE
# ============================================================
PERMIS_CODE_MAP = {
    "Moto (A)": "A",
    "Voiture légèr (B)": "B",
    "Voiture légère (B)": "B",
    "Poids lourd (C)": "C",
    "Transport en commun (D)": "D",
    "Semi-remorque (E)": "E",
    "Voiture spéciale (F)": "F",
}


def clean_permis():
    df = read_csv(SOURCE_FILES["permis_conduire"])
    df = _strip_cols(df)
    df = _clean_txt(df)

    df = df.rename(columns={
        "categories_de_permis": "categorie_permis",
        "unit": "unite",
        "date": "annee",
        "value": "valeur",
    })

    # Filtre TOTAL (sécurité)
    total_mask = df["categorie_permis"].str.lower().str.contains("total", na=False)
    if total_mask.any():
        write_csv(df[total_mask], PROCESSED_DIR / "permis_total_quarantine.csv")
        df = df[~total_mask].copy()

    # Correction typo
    df["categorie_permis"] = df["categorie_permis"].replace(
        {"Voiture légèr (B)": "Voiture légère (B)"}
    )

    # Code permis
    df["code_permis"] = df["categorie_permis"].map(PERMIS_CODE_MAP)

    df["annee"] = df["annee"].astype(int)
    df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

    # Pivot pour interpoler 2013
    pivot = df.pivot_table(
        index="annee", columns="categorie_permis", values="valeur", aggfunc="sum"
    ).sort_index()

    # Interpolation linéaire de 2013
    full_index = pd.RangeIndex(pivot.index.min(), pivot.index.max() + 1, name="annee")
    pivot = pivot.reindex(full_index)
    pivot = pivot.interpolate(method="linear", limit_direction="both")

    # Retour en long
    df_interp = pivot.reset_index().melt(
        id_vars="annee", var_name="categorie_permis", value_name="valeur"
    )

    # Ajout code_permis
    df_interp["code_permis"] = df_interp["categorie_permis"].map(PERMIS_CODE_MAP)

    # Colonne flag interpolation
    df_interp["interpolee"] = df_interp["annee"] == 2013

    df_interp = df_interp[["annee", "categorie_permis", "code_permis",
                           "valeur", "interpolee"]].sort_values(
        ["categorie_permis", "annee"]
    ).reset_index(drop=True)

    write_csv(df_interp, PROCESSED_DIR / "permis_clean.csv")
    return df_interp


def build_permis_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    wide = df_long.pivot_table(
        index="annee", columns="categorie_permis", values="valeur", aggfunc="sum"
    ).reset_index()
    wide.columns.name = None
    type_cols = [c for c in wide.columns if c != "annee"]
    wide["total"] = wide[type_cols].sum(axis=1)
    write_csv(wide, PROCESSED_DIR / "permis_wide.csv")
    return wide


# ============================================================
# 3) RESEAU_ROUTIER
# ============================================================
def clean_reseau():
    df = read_csv(SOURCE_FILES["reseau_routier"])
    df = _strip_cols(df)
    df = _clean_txt(df)
    print("Colonnes reseau_routier :", list(df.columns))   # ⬅️ debug

    df = df.rename(columns={
        "troncon": "troncon",       # déjà bon, ligne inutile mais ok
        "unit": "unite",
        "date": "annee",
        "value": "valeur",
    })

    df["annee"] = df["annee"].astype(int)
    df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
    df["etat"] = df["etat"].str.upper()

    # Catégorie (route/voirie) + revêtement (revetue/terre) depuis l'indicateur
    ind = df["indicateur"].str.upper()
    df["categorie"] = np.where(ind.str.contains("VOIRIE"), "voirie", "route")
    df["revetement"] = np.where(ind.str.contains("REVETU"), "revetue", "terre")

    # Quarantaine de la ligne "VOIRIES EN TERRE" qui est un agrégat
    agg_mask = df["troncon"].str.upper().str.strip() == "VOIRIES EN TERRE"
    if agg_mask.any():
        write_csv(df[agg_mask], PROCESSED_DIR / "reseau_routier_agregat_quarantine.csv")
        df = df[~agg_mask].copy()

    df = df[["annee", "indicateur", "categorie", "revetement",
             "troncon", "etat", "valeur", "unite"]].sort_values(
        ["categorie", "revetement", "troncon", "etat"]
    ).reset_index(drop=True)

    write_csv(df, PROCESSED_DIR / "reseau_routier_clean.csv")
    return df


# ============================================================
# 4) TRANSPORTS_TERRESTRES
# ============================================================
def clean_transports():
    df = read_csv(SOURCE_FILES["transports_terrestres"])
    df = _strip_cols(df)
    df = _clean_txt(df)

    df = df.rename(columns={
        "unit": "unite",
        "date": "annee",
        "value": "valeur",
    })
    df["annee"] = df["annee"].astype(int)
    df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

    # Slug court pour chaque indicateur
    slug_map = {
        "Accidents mortels /100.000 hab": "accidents_mortels_100k",
        "Evolution des deux roues et assimilées immatriculées": "deux_roues_immat",
        "Evolution des premières mise en circulation du parc automobile 4 roues et plus immatriculés": "premieres_mises_circulation_4r",
        "Evolution du parc automobile 4 roues et plus immatriculé": "parc_4r",
        "Evolution du volume de fret routier": "fret_routier",
        "Evolution du volume de tonne de marchandises transportées par rails": "fret_rail",
        "Nombre de blessés": "nb_blesses",
        "Nombre de cas d'accidents de la circulation": "nb_accidents",
        "Nombre de morts": "nb_morts",
        "Nombre de permis de conduire délivrés aux examens de permis de conduire": "permis_total",
        "Réseau total (chemins de fer-km)": "reseau_fer_km",
        "Trafic de véhicules de transports de marchandises sur le réseau routier": "trafic_marchandises",
        "Trafic de véhicules de transports de passagers sur le réseau routier": "trafic_passagers",
    }
    df["slug"] = df["indicateur"].map(slug_map)

    df_long = df[["annee", "indicateur", "slug", "unite", "valeur"]].sort_values(
        ["slug", "annee"]
    ).reset_index(drop=True)

    # Version wide : 1 ligne par année, 1 colonne par slug
    df_wide = df.pivot_table(
        index="annee", columns="slug", values="valeur", aggfunc="sum"
    ).reset_index()
    df_wide.columns.name = None

    write_csv(df_long, PROCESSED_DIR / "transports_clean_long.csv")
    write_csv(df_wide, PROCESSED_DIR / "transports_clean_wide.csv")
    return df_long, df_wide


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("NETTOYAGE DES DATASETS TEMPORELS")
    print("=" * 60)

    immat = clean_immatriculations()
    immat_wide = build_immatriculations_wide(immat)
    print(f"✅ immatriculations_clean     : {len(immat)} lignes")
    print(f"✅ immatriculations_wide      : {len(immat_wide)} lignes "
          f"({immat_wide['annee'].min()}-{immat_wide['annee'].max()})")

    permis = clean_permis()
    permis_wide = build_permis_wide(permis)
    print(f"✅ permis_clean               : {len(permis)} lignes")
    print(f"✅ permis_wide                : {len(permis_wide)} lignes "
          f"({permis_wide['annee'].min()}-{permis_wide['annee'].max()})")
    print(f"   - 2013 interpolé : {permis[permis['annee']==2013]['valeur'].sum():.0f} permis totaux")

    reseau = clean_reseau()
    print(f"✅ reseau_routier_clean       : {len(reseau)} lignes")

    transports_long, transports_wide = clean_transports()
    print(f"✅ transports_clean_long      : {len(transports_long)} lignes")
    print(f"✅ transports_clean_wide      : {len(transports_wide)} lignes "
          f"({transports_wide['annee'].min()}-{transports_wide['annee'].max()})")

    print("\n--- Aperçu immatriculations_wide ---")
    print(immat_wide.tail(5).to_string(index=False))
    print("\n--- Aperçu permis_wide ---")
    print(permis_wide.tail(5).to_string(index=False))
    print("\n--- Aperçu transports_wide (colonnes clés) ---")
    cols_show = ["annee", "nb_accidents", "nb_blesses", "nb_morts", "permis_total"]
    cols_show = [c for c in cols_show if c in transports_wide.columns]
    print(transports_wide[cols_show].tail(5).to_string(index=False))