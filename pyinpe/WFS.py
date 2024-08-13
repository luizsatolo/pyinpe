import requests
import geopandas as gpd
import shapely as shp
import pkg_resources
import pandas as pd
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
        self.collection = config['DETER_CERRADO_COLLECTION']
        self.layer = config['DETER_CERRADO_LAYER']
      elif self.database == "Amazonia":
        self.collection = 'deter-amz/deter_amz'
        self.layer = 'deter-amz:deter_amz'

    def __str__(self):
      global request_url 
      try:
        url = 'https://terrabrasilis.dpi.inpe.br/geoserver/'+self.collection+'/wfs?service=WFS&version=2.0.0&request=GetCapabilities'
        r = requests.get(url)
        if r.status_code == 200:
          request_url = 'https://terrabrasilis.dpi.inpe.br/geoserver/'+self.collection+'/wfs?service=WFS&version=2.0.0&srsName=EPSG:4326&request=GetFeature&typeName='+self.layer
          return f"Connected to DETER {self.database} WFS."
        else:
          request_url = None
          return f"DETER {self.database} WFS is currently unavailable. Please, try again later."
      except:
        request_url = None
        return f"Please, enter a valid database (currently, only 'Amazonia' or 'Cerrado' are allowed)."

# Function to connect to DETER WFS
def connectDeter(database: str) -> str:
  """
  Connect to Deter WFS.

  :param str database: name of Deter database. Currently supported databases are 'Amazonia' and 'Cerrado'.
  :return: a message indicating connection status
  """
  return print(Deter(database))

# Function to get a dataframe with items of DETER collections
def getAlerts(spatial_filter: int|str|list|None = None, temporal_filter: str = ['2021-01-01', '2021-06-30'], alert_type: str|None = None) -> gpd.GeoDataFrame:
  """
  Get alerts from Deter Cerrado WFS.

  :param int|str|list location: int (IBGE geocode), str ('City name - UF' or WKT geometry) or list (bounding box: [x_min, y_min, x_max, y_max]). If not specified (default), returns the alerts for all locations in the period.
  :param str date_range: start date ('yyyy-mm-dd') and end date ('yyyy-mm-dd') of the alerts
  :param alert_type str: type of the alert. Can be either 'deforestation', 'degradation' or both (default)
  :return: a geopandas GeoDataFrame with the alerts
  :rtype: gpd.GeoDataFrame
   """
  if request_url == None:
    return f"Not connected to DETER database."
  else:
    get_location = spatial_filter
    if isinstance(get_location, int):
      spatial_query = 'geocode'
      CSV_FILE = pkg_resources.resource_filename('pyinpe', '__assets__/geocode.csv')
      df_geocode = pd.read_csv(CSV_FILE, index_col = 'index').reset_index(drop = True)
      city = df_geocode.NM_MUN[df_geocode.CD_MUN == get_location].item()
      uf = df_geocode.SIGLA_UF[df_geocode.CD_MUN == get_location].item()
      location = 'municipality=%27'+city+'%27%20AND%20uf=%27'+uf+'%27%20AND%20'
    elif isinstance(get_location, str):
      if ' - ' in get_location:
        spatial_query = 'city_name'
        location = 'municipality=%27'+get_location.split('-')[0].strip()+'%27%20AND%20uf=%27'+get_location.split('-')[1].strip()+'%27%20AND%20'
      elif 'POLYGON' in get_location:
        spatial_query = 'polygon'
        s = gpd.GeoSeries.from_wkt([get_location])
        location = 'BBOX(st_multi,'+str(s[0].bounds).replace('(','').replace(')','').replace(' ','')+',%27EPSG:4674%27)%20AND%20'
      else:
        spatial_query = 'invalid'
        location = ''
    elif isinstance(get_location, list):
      spatial_query = 'bbox'
      location = 'BBOX(st_multi,'+str(get_location).replace('[','').replace(']','').replace(' ','')+',%27EPSG:4674%27)%20AND%20'
    else:
      spatial_query = 'none'
      location = ''
    start_date = temporal_filter[0]
    end_date = temporal_filter[1]
    get_type = alert_type
    if get_type == 'degradation':
      get_classname = '%20AND%20classname=%27DEGRADACAO%27'
    elif get_type == 'deforestation':
      get_classname = '%20AND%20classname=%27DESMATAMENTO_CR%27%20OR%20classname=%27DESMATAMENTO_VEG%27'
    else:
      get_classname = ''
    try:
      url = request_url+'&CQL_FILTER='+location+'view_date%20BETWEEN%20%27'+start_date+'%27%20AND%20%27'+end_date+'%27'+get_classname+'&outputFormat=json&sortBy=gid&startIndex=0'
      r = requests.get(url)
      j = r.json()
      df = gpd.GeoDataFrame.from_features(j)
      if spatial_query == 'polygon':
        return df.loc[df.overlaps(shp.from_wkt(get_location))].reset_index(drop=True)
      else:
        return df
    except:
      return f"Invalid filters. Please, see the documentation for examples."
    
class Queimadas:

  def __init__(self):
    self.database = 'Queimadas'

  def __str__(self):
    global request_url
    try:
      url = 'https://terrabrasilis.dpi.inpe.br/queimadas/geoserver/dados_abertos/wfs?SERVICE=WFS&VERSION=2.0.0&REQUEST=Getcapabilities'
      r = requests.get(url)
      if r.status_code == 200:
        request_url = 'https://terrabrasilis.dpi.inpe.br/queimadas/geoserver/dados_abertos/wfs?SERVICE=WFS&VERSION=2.0.0&srsName=EPSG:4326&REQUEST=GetFeature&typeName='
        return f"Connected to {self.database} WFS."
      else:
        request_url = None
        return f"{self.database} WFS is currently unavailable. Please, try again later."
    except:
      request_url = None
      return f"Invalid argument (0 argument expected)"

# Function to connect to Queimadas WFS
def connectQueimadas() -> str:
  """
  Connect to Queimadas WFS.

  :return: a message indicating connection status
  """
  return print(Queimadas())

# Function to get a dataframe with items of Queimadas collections
def getFires(spatial_filter: int|str|list|None = None, temporal_filter: str = ['2021-01-01', '2021-06-30']) -> gpd.GeoDataFrame:
  """
  Get fires from Queimadas WFS.

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
    if isinstance(get_location, int):
      spatial_query = 'geocode'
      location = 'id_2='+str(get_location)+'%20AND%20'
    elif isinstance(get_location, str):
      if ' - ' in get_location:
        spatial_query = 'city_name'
        uf = df_estado.estado[df_estado.sigla == get_location.split('-')[1].strip()].item()
        location = 'municipio=%27'+get_location.split('-')[0].strip().upper()+'%27%20AND%20estado=%27'+uf+'%27%20AND%20'
      elif 'POLYGON' in get_location:
        spatial_query = 'polygon'
        s = gpd.GeoSeries.from_wkt([get_location])
        location = 'BBOX(geometria,'+str(s[0].bounds).replace('(','').replace(')','').replace(' ','')+',%27EPSG:4326%27)%20AND%20'
      else:
        spatial_query = 'invalid'
        location = ''
    elif isinstance(get_location, list):
      spatial_query = 'bbox'
      location = 'BBOX(geometria,'+str(get_location).replace('[','').replace(']','').replace(' ','')+',%27EPSG:4326%27)%20AND%20'
    else:
      spatial_query = 'none'
      location = ''
    start_date = temporal_filter[0]
    end_date = temporal_filter[1]
    start_year = start_date[:4]
    end_year = end_date[:4]

    df = gpd.GeoDataFrame(columns=['geometry', 'id_foco_bdq', 'foco_id', 'longitude', 'latitude',
       'data_hora_gmt', 'data_pas', 'satelite', 'municipio', 'estado', 'pais',
       'precipitacao', 'numero_dias_sem_chuva', 'risco_fogo', 'bioma', 'id_0',
       'id_1', 'id_2', 'continente_id', 'vegetacao', 'frp', 'bbox'], geometry='geometry')
    
    try:
      for t in range(int(start_year), int(end_year)+1):
        url = request_url+'dados_abertos:focos_'+str(t)+'_br_satref&CQL_FILTER='+location+'data_hora_gmt%20BETWEEN%20%27'+start_date+'%27%20AND%20%27'+end_date+'%27&outputFormat=json'
        #url = request_url+'&CQL_FILTER='+location+'data_hora_gmt%20BETWEEN%20%27'+start_date+'%27%20AND%20%27'+end_date+'%27&outputFormat=json&sortBy=gid&startIndex=0'
        r = requests.get(url)
        j = r.json()
        temp_df = gpd.GeoDataFrame.from_features(j)
        df = pd.concat([df, temp_df]).reset_index(drop = True)
      if spatial_query == 'polygon':
        return df.loc[df.within(shp.from_wkt(get_location))].reset_index(drop=True)
      else:
        return df
    except:
      return f"Invalid filters. Please, see the documentation for examples."