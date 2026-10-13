import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.config import SOURCE_FILES

df = pd.read_csv(SOURCE_FILES["immatriculations_2"], encoding="utf-8")

# Série complète pour "Voitures"
voit = df[df["types-de-vehicule"] == "Voitures"].sort_values("Date")
print("=== Série Voitures (toutes années) ===")
print(voit[["Date", "Value"]].to_string(index=False))

print("\n=== Variations annuelles (Voitures) ===")
voit = voit.copy()
voit["delta"] = voit["Value"].diff()
print(voit[["Date", "Value", "delta"]].to_string(index=False))

print("\n=== Nombre d'années où Value baisse vs monte ===")
print(f"Baisses : {(voit['delta'] < 0).sum()}")
print(f"Hausses : {(voit['delta'] > 0).sum()}")

# Si c'est un flux : variations = immatriculations nettes (petits nombres)
# Si c'est un parc : variations = ajouts nets (petits nombres) et Value = gros cumul