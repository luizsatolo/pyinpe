import requests
import geopandas as gpd
import shapely as shp
import pkg_resources
import pandas as pd
import numpy as np
import warnings
import json

warnings.simplefilter(action='ignore', category=FutureWarning)


JSON_FILE = pkg_resources.resource_filename('pyinpe', '__assets__/config.json')
with open(JSON_FILE) as config_file:
    config = json.load(config_file)
    
class Deter:

    def __init__(self, database):
      self.database = database
      self.collection = None
      if self.database == "Cerrado":
        self.collection = 'deter_cerrado'
      elif self.database == "Amazonia":
        self.collection = 'deter_amz'

    def __str__(self):
      global request_url
      try:
        url = config['API_URL']+'?f=json&lang=en-US'
        r = requests.get(url)
        if r.status_code == 200:
          request_url = config['API_URL']+'collections/'+self.collection+'/items?f=json&sortby='+config['DETER_DATE_VAR']+'&startIndex=0&lang=en-US&limit=1000000&additionalProp1=%7B%7D&skipGeometry=false&offset=0&filter-lang=cql-text&filter='
          return f"Connected to DETER {self.database} OGC API Features."
        else:
          request_url = None
          return f"DETER {self.database} OGC API Features is currently unavailable. Please, try again later."
      except:
        request_url = None
        return f"Please, enter a valid database (currently, only 'Amazonia' or 'Cerrado' are allowed)."

# Function to connect to DETER Collection
def connectDeter(database: str) -> str:
  """
  Connect to Deter WFS.

  :param str database: name of Deter database. Currently supported databases are 'Amazonia' and 'Cerrado'.
  :return: a message indicating connection status
  """
  return print(Deter(database))

# Function to get a dataframe with items of DETER collections
def getAlerts(spatial_filter: int|str|list|None = None, temporal_filter: str = ['2020-12-31', '2021-06-30'], alert_type: str|None = None) -> gpd.GeoDataFrame:
  """
  Get alerts from Deter OGC API Features.

  :param int|str|list location: int (IBGE geocode), str ('City name - UF' or WKT geometry) or list (bounding box: [x_min, y_min, x_max, y_max]). If not specified (default), returns the alerts for all locations in the period.
  :param str date_range: start date ('yyyy-mm-dd') and end date ('yyyy-mm-dd') of the alerts
  :param alert_type str: type of the alert. Can be either 'deforestation', 'degradation' or both (default)
  :return: a geopandas GeoDataFrame with the alerts
  :rtype: gpd.GeoDataFrame
   """
  if request_url == None:
    return f"Not connected to any database."
  else:
    get_location = spatial_filter
    if isinstance(get_location, (int, np.int64)):
      spatial_query = 'geocode'
      CSV_FILE = pkg_resources.resource_filename('pyinpe', '__assets__/geocode.csv')
      df_geocode = pd.read_csv(CSV_FILE, index_col = 'index').reset_index(drop = True)
      city = df_geocode.NM_MUN[df_geocode.CD_MUN == get_location].item()
      uf = df_geocode.SIGLA_UF[df_geocode.CD_MUN == get_location].item()
      location = config['API_DETER_CITY_VAR']+'=%27'+city+'%27%20AND%20'+config['DETER_STATE_VAR']+'=%27'+uf+'%27'
    elif isinstance(get_location, str):
      if ' - ' in get_location:
        spatial_query = 'city_name'
        location = config['API_DETER_CITY_VAR']+'=%27'+get_location.split('-')[0].strip().upper()+'%27%20AND%20'+config['DETER_STATE_VAR']++'=%27'+get_location.split('-')[1].strip()+'%27'
      elif 'POLYGON' in get_location:
        spatial_query = 'polygon'
        location = 'WITHIN(geometry,'+get_location+')'
      else:
        spatial_query = 'invalid'
        location = ''
    elif isinstance(get_location, list):
      spatial_query = 'bbox'
      location = 'BBOX(geometry,'+str(get_location).replace('[','').replace(']','').replace(' ','')+')'
    else:
      spatial_query = 'none'
      location = ''
    start_date = temporal_filter[0]
    end_date = temporal_filter[1]
    get_type = alert_type
    if get_type == 'degradation':
      get_classname = '%20AND%20'+config['DETER_TYPE_VAR']+'=%27'+config['DETER_DEGRADATION_TYPE']+'%27'
    elif get_type == 'deforestation':
      get_classname = '%20AND%20'+config['DETER_TYPE_VAR']+'=%27'+config['DETER_DEFORESTATION_TYPE1']+'%27%20OR%20'+config['DETER_TYPE_VAR']+'=%27'+config['DETER_DEFORESTATION_TYPE2']+'%27'
    else:
      get_classname = ''
    try:
      url = request_url+location+get_classname+'%20AND%20'+config['DETER_DATE_VAR']+'%20DURING%20'+start_date+'T00:00:00Z/'+end_date+'T23:59:59Z'
      r = requests.get(url)
      j = r.json()
      df = gpd.GeoDataFrame.from_features(j)
      return df
    except:
      return f"Invalid filters. Please, see the documentation for examples."
    

class Queimadas:

  def __init__(self):
    self.database = 'Queimadas'

  def __str__(self):
    global request_url
    try:
      url = config['API_URL']+'?f=json&lang=en-US'
      r = requests.get(url)
      if r.status_code == 200:
        request_url = config['API_URL']+'collections/'+config['API_QUEIMADAS_COLLECTION']+'/items?f=json&sortby='+config['API_QUEIMADAS_DATE_VAR']+'&startIndex=0&lang=en-US&limit=1000000&additionalProp1=%7B%7D&skipGeometry=false&offset=0&filter-lang=cql-text&filter=satelite=%27'+config['API_QUEIMADAS_SATELLITE']+'%27%20AND%20'
        return f"Connected to {self.database} OGC API Features."
      else:
        request_url = None
        return f"{self.database} OGC API Features is currently unavailable. Please, try again later."
    except:
      request_url = None
      return f"Invalid argument (0 argument expected)"

# Function to connect to Queimadas Collection
def connectQueimadas() -> str:
  """
  Connect to Queimadas OGC API Features.

  :return: a message indicating connection status
  """
  return print(Queimadas())

# Function to get a dataframe with items of Queimadas collection
def getFires(spatial_filter: int|str|list|None = None, temporal_filter: str = ['2024-01-01', '2024-06-30']) -> gpd.GeoDataFrame:
  """
  Get fires from Queimadas OGC API Features.

  :param int|str|list location: int (IBGE geocode), str ('City name - UF' or WKT geometry) or list (bounding box: [x_min, y_min, x_max, y_max]). If not specified (default), returns the alerts for all locations in the period.
  :param str date_range: start date ('yyyy-mm-dd') and end date ('yyyy-mm-dd') of the alerts
  :return: a geopandas GeoDataFrame with the fires
  :rtype: gpd.GeoDataFrame
   """
  if request_url == None:
    return f"Not connected to any database."
  else:
    df_estado = pd.DataFrame({'estado': ['ACRE', 'ALAGOAS', 'AMAPÁ', 'AMAZONAS', 'BAHIA', 'CEARÁ', 'DISTRITO FEDERAL', 'ESPÍRITO SANTO', 'GOIÁS', 'MARANHÃO', 'MATO GROSSO', 'MATO GROSSO DO SUL', 'MINAS GERAIS', 'PARÁ', 'PARAÍBA', 'PARANÁ', 'PERNAMBUCO', 'PIAUÍ', 'RIO DE JANEIRO', 'RIO GRANDE DO NORTE', 'RIO GRANDE DO SUL', 'RONDÔNIA', 'RORAIMA', 'SANTA CATARINA', 'SÃO PAULO', 'SERGIPE', 'TOCANTINS'],
                              'sigla': ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']})
    get_location = spatial_filter
    if isinstance(get_location, (int, np.int64)):
      spatial_query = 'geocode'
      CSV_FILE = pkg_resources.resource_filename('pyinpe', '__assets__/geocode.csv')
      df_geocode = pd.read_csv(CSV_FILE, index_col = 'index').reset_index(drop = True)
      city = df_geocode.NM_MUN[df_geocode.CD_MUN == get_location].item()
      uf = df_geocode.SIGLA_UF[df_geocode.CD_MUN == get_location].item()
      location = config['QUEIMADAS_CITY_VAR']+'=%27'+city+'%27%20AND%20'+config['QUEIMADAS_STATE_VAR']+'=%27'+uf+'%27'
    elif isinstance(get_location, str):
      if ' - ' in get_location:
        spatial_query = 'city_name'
        uf = df_estado.estado[df_estado.sigla == get_location.split('-')[1].strip()].item()
        location = config['QUEIMADAS_CITY_VAR']+'=%27'+get_location.split('-')[0].strip().upper()+'%27%20AND%20'+config['QUEIMADAS_STATE_VAR']+'=%27'+uf+'%27'
      elif 'POLYGON' in get_location:
        spatial_query = 'polygon'
        location = 'WITHIN(geometry,'+get_location+')'
      else:
        spatial_query = 'invalid'
        location = ''
    elif isinstance(get_location, list):
      spatial_query = 'bbox'
      location = 'BBOX(geometry,'+str(get_location).replace('[','').replace(']','').replace(' ','')+')'
    else:
      spatial_query = 'none'
      location = ''
    start_date = temporal_filter[0]
    end_date = temporal_filter[1]
    start_year = start_date[:4]
    end_year = end_date[:4]

    try:
      url = request_url+location+'%20AND%20'+config['API_QUEIMADAS_DATE_VAR']+'%20DURING%20'+start_date+'T00:00:00Z/'+end_date+'T23:59:59Z'
      r = requests.get(url)
      j = r.json()
      df = gpd.GeoDataFrame.from_features(j)
      return df
    except:
      return f"Invalid filters. Please, see the documentation for examples."