import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.config import SOURCE_FILES


def diag(name, path):
    print(f"\n{'='*78}\n📄 {name}  →  {path.name}\n{'='*78}")
    df = pd.read_csv(path, encoding="utf-8")
    print(f"Shape          : {df.shape}")
    print(f"Colonnes       : {list(df.columns)}")
    print(f"Types          :\n{df.dtypes.to_string()}")

    print(f"\nValeurs manquantes par colonne :")
    print(df.isna().sum().to_string())

    # Colonnes catégorielles : valeurs uniques
    for col in df.columns:
        nun = df[col].nunique(dropna=True)
        if nun <= 20:
            print(f"\n▸ {col} ({nun} valeurs uniques) :")
            print(sorted(df[col].dropna().unique().tolist()))

    # Colonnes numériques : min / max
    num_cols = df.select_dtypes("number").columns
    if len(num_cols):
        print(f"\nStats numériques :")
        print(df[num_cols].describe().T[["min", "max", "mean"]].to_string())

    print(f"\n5 premières lignes :")
    print(df.head(5).to_string())

    print(f"\n5 dernières lignes :")
    print(df.tail(5).to_string())


diag("immatriculations_2",     SOURCE_FILES["immatriculations_2"])
diag("permis_conduire",        SOURCE_FILES["permis_conduire"])
diag("reseau_routier",         SOURCE_FILES["reseau_routier"])
diag("transports_terrestres",  SOURCE_FILES["transports_terrestres"])