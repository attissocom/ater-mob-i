"""
Utilitaires géométriques pour le réseau routier.
- parsing WKT
- calcul de longueur en km (projection UTM 31N pour le Togo)
"""
import pandas as pd
import shapely.wkt as swkt
import geopandas as gpd


def parse_geom(s):
    """Parse un WKT en géométrie shapely. Renvoie None si invalide."""
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        return swkt.loads(s)
    except Exception:
        return None


def compute_route_lengths(df: pd.DataFrame, geom_col: str = "geometry") -> pd.DataFrame:
    """
    Ajoute une colonne 'longueur_km' à un DataFrame contenant une colonne WKT.
    Utilise une projection métrique UTM 31N (EPSG:32631), adaptée au Togo.
    """
    df = df.copy()
    geoms = df[geom_col].apply(parse_geom)
    gdf = gpd.GeoDataFrame(df, geometry=geoms, crs="EPSG:4326")
    gdf_m = gdf.to_crs("EPSG:32631")
    df["longueur_km"] = gdf_m.geometry.length / 1000.0
    return df