import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.config import PROCESSED_DIR, SOURCE_FILES

for f in ["immatriculations_wide.csv", "permis_wide.csv",
          "transports_clean_wide.csv"]:
    df = pd.read_csv(PROCESSED_DIR / f, encoding="utf-8", nrows=2)
    print(f"\n{f}")
    print(f"  Colonnes : {list(df.columns)}")
    print(f"  Types    : {dict(df.dtypes.astype(str))}")