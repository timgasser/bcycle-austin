# Common library routines for the BCycle analysis
import pandas as pd
import numpy as np

INPUT_DIR = '../input'


def load_bikes(file=INPUT_DIR + '/bikes.csv'):
    '''
    Load the bikes CSV file, converting column types
    INPUT: Filename to read (defaults to `../input/bikes.csv`
    RETURNS: Pandas dataframe containing bikes information
    '''
    bikes_df = pd.read_csv(file,
                          dtype={'station_id' : np.int8,
                                 'bikes' : np.int8,
                                 'docks' : np.int8}
                           )
    bikes_df['datetime'] = pd.to_datetime(bikes_df['datetime'], format='%Y-%m-%d %H:%M:%S')
    return bikes_df
    

def load_stations(file=INPUT_DIR + '/stations.csv'):
    '''
    Load the stations CSV file, converting column types
    INPUT: Filename to read (defaults to `../input/stations.csv`
    RETURNS: Pandas dataframe containing stations information
    '''
    stations_df = pd.read_csv(file,
                              dtype={'station_id' : np.int8,
                                 'lat' : np.float32,
                                 'lon' : np.float32}
                              )
    stations_df['datetime'] = pd.to_datetime(stations_df['datetime'], format='%Y-%m-%d %H:%M:%S')                           
    return stations_df

def load_weather(file=INPUT_DIR + '/weather.csv'):
    '''Loads the weather CSV and converts types'''
    df = pd.read_csv(file)
    
    # Remove whitespace and keep min/max values
    df.columns = [col.strip() for col in df.columns]
    df = df[['CDT','Max TemperatureF','Min TemperatureF', 
             'Max Humidity', 'Min Humidity',
             'Max Sea Level PressureIn', 'Min Sea Level PressureIn', 
             'Max Wind SpeedMPH', 'Mean Wind SpeedMPH', 'Max Gust SpeedMPH',
             'PrecipitationIn', 'CloudCover', 'Events']]
    
    # Clean up column names, drop means as they're a linear combination of max/min
    df.columns = ['date', 'max_temp', 'min_temp', 'max_humidity', 'min_humidity',
                 'max_pressure', 'min_pressure', 'max_wind', 'min_wind', 'max_gust',
                 'precipitation', 'cloud_cover', 'events']
    
    # Convert column types appropriately
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')  
    df.index = df['date']
    df = df.drop('date', axis=1)
    
    df[['max_temp', 'min_temp']] = df[['max_temp', 'min_temp']].astype(np.uint8)
    df[['max_humidity', 'min_humidity']] = df[['max_humidity', 'min_humidity']].astype(np.uint8)
    df[['max_wind', 'min_wind', 'max_gust']] = df[['max_wind', 'min_wind', 'max_gust']].astype(np.uint8)


    # Cloud cover is a fraction of 8 - 
    # http://help.wunderground.com/knowledgebase/articles/129043-how-can-i-translate-the-cloud-cover-data-on-your
    df['cloud_pct'] = (df['cloud_cover'].astype(np.float32) / 8.0) * 100
    df = df.drop('cloud_cover', axis=1)
    
    # Precipitation sometimes has 'T' for trace amounts of rain. Replace this with small value
    # and convert to a float
    # http://help.wunderground.com/knowledgebase/articles/656875-what-does-t-stand-for-on-the-rain-precipitation
    df['precipitation'] = df['precipitation'].replace('T', 0.01)
    df['precipitation'] = df['precipitation'].astype(np.float32)

    # Events are tricky. they're separated by hypens, and can have multiple values not in the same order !
    events = set()
    df['events'] = df['events'].replace(np.nan, 'None')
    for row in df['events']:
        if row is not np.nan:
            line = row.split('-')
            [events.add(word.lower()) for word in line]
    
    for event in events:
        df[event] = df['events'].apply(str.lower).str.contains(event)
    
    df = df.drop(['events', 'none'], axis=1)
    return df


def haversine_dist(lat1, lon1, lat2, lon2, R=3961):
    '''
    Calculates the distance between two points in miles using the haversine formula
    INPUT: lat1/lon1 and lat2/lon2 are position values
           R is an optional radius of the planet 
    RETURNS: Distance between the points in miles
    '''
    
    dlon = np.radians(lon2 - lon1)
    dlat = np.radians(lat2 - lat1)
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)
    a = (np.sin(dlat/2.0))**2 + np.cos(lat1) * np.cos(lat2) * (np.sin(dlon/2.0))**2
    c = 2 * np.arctan2( np.sqrt(a), np.sqrt(1-a) )
    d = R * c
    
    return d

