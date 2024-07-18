"""Main module."""
import owslib
from owslib.wfs import WebFeatureService


def get_contents(driver='wfs', version='2.0.0', database='queimadas'):
    """Returns the contents of the database in the driver
    """
    if driver == 'wfs':
        if database == 'queimadas':
            wfs_url = 'https://terrabrasilis.dpi.inpe.br/queimadas/geoserver/wfs'
            wfs = WebFeatureService(wfs_url, version=version)
            return list(wfs.contents)
        else:
            return print('Database not found')
    else:
        return print('Driver not available')