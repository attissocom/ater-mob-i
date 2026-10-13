"""Calcul des surfaces (km²) des régions et préfectures à partir des GeoJSON."""
import geopandas as gpd
import pandas as pd

from src.config import GEOJSON_FILES, PROCESSED_DIR
from src.io_utils import write_csv


def compute_areas(level="region"):
    """Renvoie un DataFrame (region, [prefecture], area_km2)."""
    if level == "region":
        gdf = gpd.read_file(GEOJSON_FILES["regions"])
        gdf = gdf.to_crs("EPSG:32631")
        gdf["area_km2"] = gdf.geometry.area / 1e6
        gdf["region_canon"] = (
            gdf["NAME_1"].str.strip().str.lower()
            .replace({"centre": "centrale"})
        )
        out = gdf[["region_canon", "area_km2"]].rename(columns={"region_canon": "region"})

    elif level == "prefecture":
        gdf = gpd.read_file(GEOJSON_FILES["prefectures"])
        gdf = gdf.to_crs("EPSG:32631")
        gdf["area_km2"] = gdf.geometry.area / 1e6
        gdf["region"] = (
            gdf["NAME_1"].str.strip().str.lower()
            .replace({"centre": "centrale"})
        )
        gdf["prefecture"] = (
            gdf["NAME_2"].str.strip().str.lower()
            .str.replace("-", " ", regex=False)
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore").str.decode("utf-8")
            .str.replace(r"\s+", " ", regex=True)
        )
        out = gdf[["region", "prefecture", "area_km2"]]

    else:
        raise ValueError(level)

    return out


def build_areas():
    regions = compute_areas("region")
    prefs = compute_areas("prefecture")
    write_csv(regions, PROCESSED_DIR / "areas_regions.csv")
    write_csv(prefs, PROCESSED_DIR / "areas_prefectures.csv")
    return regions, prefs


if __name__ == "__main__":
    r, p = build_areas()
    print(f"✅ areas_regions      : {len(r)} régions")
    print(f"✅ areas_prefectures  : {len(p)} préfectures")
    print(r.to_string(index=False))