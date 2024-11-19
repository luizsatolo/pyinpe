import pkg_resources
import geopandas as gpd
import fiona

fiona.drvsupport.supported_drivers['shp'] = 'rw' # enable shp support which is disabled by default
fiona.drvsupport.supported_drivers['SHP'] = 'rw'

def load_shapefile():
    """Return a geodataframe with the polygon from a shapefile.
    """
    stream = pkg_resources.resource_stream(__name__, 'data/polygon.shp')
    return gpd.read_file(stream, encoding='latin-1', driver='SHP')