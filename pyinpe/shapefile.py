import pkg_resources
import geopandas as gpd
from pyogrio import write_dataframe


def load_shapefile():
    """Return a geodataframe with the polygon from a shapefile.
    """
    stream = pkg_resources.resource_stream(__name__, 'data/polygon.shp')
    write_dataframe(df, stream)
    return df