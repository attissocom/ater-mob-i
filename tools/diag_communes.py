import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_utils import read_csv
from src.config import SOURCE_FILES, GEO_REFERENCE_PATH

# 1. Voir ce que contient le référentiel pour les préfectures en question
ref = read_csv(GEO_REFERENCE_PATH)

for pref in ["danyi", "kozah", "agoé nyive", "agoe nyive", "golfe", "kloto", "agou"]:
    sub = ref[ref["prefecture"] == pref]
    if len(sub):
        print(f"\n=== Préfecture : {pref} ===")
        print(sub[["region", "prefecture", "commune", "canton", "population"]].to_string(index=False))