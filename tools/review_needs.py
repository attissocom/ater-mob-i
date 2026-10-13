import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.config import CROSSWALK_PATH, OVERRIDES_PATH
from src.io_utils import write_csv

cw = pd.read_csv(CROSSWALK_PATH, encoding="utf-8")

nr = cw[cw["needs_review"]].copy()
nr = nr.sort_values(["dataset_source", "niveau", "score"], ascending=[True, True, False])

print(f"=== {len(nr)} cas à valider ===\n")
for (src, niv), grp in nr.groupby(["dataset_source", "niveau"]):
    print(f"\n--- {src} / {niv} ({len(grp)} cas) ---")
    print(grp[["name_source", "name_normalized", "name_canonical", "score",
               "region", "prefecture", "commune"]].to_string(index=False))

# Génère un squelette d'overrides pré-rempli
override_rows = []
for _, r in nr.iterrows():
    override_rows.append({
        "dataset_source": r["dataset_source"],
        "niveau": r["niveau"],
        "name_normalized": r["name_normalized"],
        "name_canonical": "",          # À REMPLIR : nom canonique correct
        "region": r["region"] if pd.notna(r["region"]) else "",
        "prefecture": r["prefecture"] if pd.notna(r["prefecture"]) else "",
        "commune": r["commune"] if pd.notna(r["commune"]) else "",
        "canton": r["canton"] if pd.notna(r["canton"]) else "",
        "commentaire": f"score={r['score']} | source={r['name_source']}",
    })

template = pd.DataFrame(override_rows)

print("\n\n=== Squelette d'overrides généré ===")
print(template.to_string(index=False))

# Écrit un fichier de travail
template_path = OVERRIDES_PATH.parent / "geo_crosswalk_overrides_TEMPLATE.csv"
write_csv(template, template_path)
print(f"\n📄 Template écrit dans : {template_path}")
print("   → À remplir (colonne name_canonical) puis renommer/écraser geo_crosswalk_overrides.csv")