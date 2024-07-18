import owslib
from owslib.wfs import WebFeatureService

# Object for WFS functions and parameters

class WFS:

  def __init__(self, version, database, collection=None):
    self.version = version
    self.database = database
    self.collection = collection

  def wfs_url(self):
    """Returns the contents of the database in the driver
    """
    if self.database == 'queimadas':
      self.wfs_url = 'https://terrabrasilis.dpi.inpe.br/queimadas/geoserver/wfs'
    elif self.database == 'deter_amz':
      self.wfs_url = 'https://terrabrasilis.dpi.inpe.br/geoserver/deter-amz/deter_amz/wfs'
    elif self.database == 'deter_cerrado':
      self.wfs_url = 'https://terrabrasilis.dpi.inpe.br/geoserver/deter-cerrado/deter_cerrado/wfs'
    return self.wfs_url

  def wfs(self):
    self.wfs = WebFeatureService(self.wfs_url(), version=self.version)
    return self.wfs

  def wfs_contents(self):
    self.contents = self.wfs().contents
    return self.contents

  def collection_schema(self):
    if self.collection is not None:
      self.schema = self.wfs().get_schema(self.collection)
      return self.schema
    
# Function to get the collections of a WFS database
def get_contents(version = '2.0.0', database = 'queimadas'):
  service = WFS(version, database)
  return list(service.wfs_contents())

# Function to get the schema of a collection in the WFS database
def get_collectionSchema(version = '2.0.0', database = 'queimadas', collection='dados_abertos:focos_2023_br_satref'):
  service = WFS(version, database, collection)
  return service.collection_schema()