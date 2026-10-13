"""
Résolution spatiale robuste :
- parse n'importe quelle géométrie WKT (POINT, LINESTRING, POLYGON, MULTI*)
- pour les lignes/polygones, utilise representative_point() pour le test within
- renvoie region_spatial et prefecture_spatial canoniques (RGPH5)
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt as shapely_wkt
from shapely.geometry import Point

from src.config import (
    GEOJSON_FILES, GEOJSON_REGION_COL, GEOJSON_PREF_REGION, GEOJSON_PREF_NAME,
    GADM_TO_RGPH5_REGION,
)
from src.geo_normalize import normalize_series


def parse_wkt_geom(val):
    """Retourne un objet shapely à partir d'une chaîne WKT. None si invalide."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in {"nan", "none"}:
        return None
    try:
        return shapely_wkt.loads(s)
    except Exception:
        return None


def _repr_point(geom):
    """Point représentatif pour le test within (point, ligne ou polygone)."""
    if geom is None:
        return None
    try:
        if geom.is_empty:
            return None
        return geom.representative_point()
    except Exception:
        return None


def load_regions_gdf() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(GEOJSON_FILES["regions"])
    gdf["region_norm"] = normalize_series(gdf[GEOJSON_REGION_COL])
    gdf["region_canonical"] = (
        gdf["region_norm"].map(GADM_TO_RGPH5_REGION).fillna(gdf["region_norm"])
    )
    return gdf[["region_canonical", "geometry"]]


def load_prefectures_gdf() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(GEOJSON_FILES["prefectures"])
    gdf["region_norm"] = normalize_series(gdf[GEOJSON_PREF_REGION])
    gdf["prefecture_norm"] = normalize_series(gdf[GEOJSON_PREF_NAME])
    gdf["region_canonical"] = (
        gdf["region_norm"].map(GADM_TO_RGPH5_REGION).fillna(gdf["region_norm"])
    )
    return gdf[["region_canonical", "prefecture_norm", "geometry"]]


def resolve_points(df: pd.DataFrame, geom_col: str) -> pd.DataFrame:
    """
    Enrichit df avec :
      - geom_valid         : booléen, True si la géométrie a été parsée
      - region_spatial     : région canonique (RGPH5)
      - prefecture_spatial : préfecture normalisée
    """
    df = df.copy()
    geoms = df[geom_col].apply(parse_wkt_geom)
    df["geom_valid"] = geoms.notna()

    df["region_spatial"] = None
    df["prefecture_spatial"] = None

    valid_mask = df["geom_valid"]
    if not valid_mask.any():
        return df

    repr_pts = geoms[valid_mask].apply(_repr_point)
    inner_mask = repr_pts.notna()
    if not inner_mask.any():
        return df

    idx = repr_pts[inner_mask].index
    pts = gpd.GeoDataFrame(
        df.loc[idx].copy(),
        geometry=list(repr_pts.loc[idx]),
        crs="EPSG:4326",
    )

    pref = load_prefectures_gdf()

    joined = gpd.sjoin(
        pts,
        pref[["region_canonical", "prefecture_norm", "geometry"]],
        how="left",
        predicate="within",
    ).drop(columns=["index_right"], errors="ignore")

    df.loc[idx, "region_spatial"] = joined["region_canonical"].values
    df.loc[idx, "prefecture_spatial"] = joined["prefecture_norm"].values
    return df