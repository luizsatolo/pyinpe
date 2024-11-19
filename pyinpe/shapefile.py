import pkg_resources
import geopandas as gpd
import pyogrio

pyogrio.core._register_drivers()

def load_shapefile():
    """Return a geodataframe with the polygon from a shapefile.
    """
    stream = pkg_resources.resource_stream(__name__, 'data/polygon.shp')
    return gpd.read_file(stream, encoding='latin-1')