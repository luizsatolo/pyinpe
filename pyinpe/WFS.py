import requests
import geopandas as gpd
import shapely as shp

def connectDeter() -> str:
  """
  Connect to Deter Cerrado WFS.

  :return: a message indicating connection status
  """
  try:
    url = 'https://terrabrasilis.dpi.inpe.br/geoserver/deter-cerrado/deter_cerrado/wfs?service=WFS&version=2.0.0&request=GetCapabilities'
    r = requests.get(url)
    if r.status_code == 200:
      return print('Connected to DETER Cerrado WFS.')
    else: 
      return print('DETER Cerrado WFS is currently unavailable. Please, try again later.')
  except:
    return print('DETER Cerrado WFS is currently unavailable. Please, try again later.')
  
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
  get_location = spatial_filter 
  if isinstance(get_location, str):
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
  url = 'https://terrabrasilis.dpi.inpe.br/geoserver/deter-cerrado/deter_cerrado/wfs?service=WFS&version=2.0.0&srsName=EPSG:4326&request=GetFeature&typeName=deter-cerrado:deter_cerrado&CQL_FILTER='+location+'view_date%20BETWEEN%20%27'+start_date+'%27%20AND%20%27'+end_date+'%27'+get_classname+'&outputFormat=json&sortBy=gid&startIndex=0'
  r = requests.get(url)
  j = r.json()
  df = gpd.GeoDataFrame.from_features(j)
  if spatial_query == 'polygon':
    return df.loc[df.overlaps(shp.from_wkt(get_location))].reset_index(drop=True)
  else:
    return df