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

def load_bike_trips():
    # Sort the bikes_df dataframe by station_id first, and then datetime so we
    # can use a diff() and get the changes by time for each station
    bikes_df = load_bikes()
    bikes_df = bikes_df.sort_values(['station_id', 'datetime']).copy()
    stations = bikes_df['station_id'].unique()

    # Our dataframe is grouped by station_id first now, so grab each station in
    # turn and do a diff() on bikes and docks for each station individually
    diff_list = list()
    for station in stations:
        station_diff_df = bikes_df[bikes_df['station_id'] == station].copy()
        station_diff_df['bikes_diff'] = station_diff_df['bikes'].diff()
        station_diff_df['docks_diff'] = station_diff_df['docks'].diff()
        diff_list.append(station_diff_df)

    # Concatenate the station dataframes back together into a single one.
    # Make sure we didn't lose any rows in the process (!)
    bikes_diff_df = pd.concat(diff_list)

    # The first row of each station-wise diff is filled with NaNs, store a 0 in these fields
    # then we can convert the data type from floats to int8s 
    bikes_diff_df.fillna(0, inplace=True)
    bikes_diff_df[['bikes_diff', 'docks_diff']] = bikes_diff_df[['bikes_diff', 'docks_diff']].astype(np.int8)
    bikes_diff_df.index = bikes_diff_df['datetime']
    bikes_diff_df.drop('datetime', axis=1, inplace=True)
    assert(bikes_df.shape[0] == bikes_diff_df.shape[0]) 

    bike_trips_df = bikes_diff_df
    bike_trips_df['checkouts'] = bike_trips_df['bikes_diff']
    bike_trips_df.loc[bike_trips_df['checkouts'] > 0, 'checkouts'] = 0
    bike_trips_df['checkouts'] = bike_trips_df['checkouts'].abs()

    # Conversely, checkins are positive `bikes_diff` values
    bike_trips_df['checkins'] = bike_trips_df['bikes_diff']
    bike_trips_df.loc[bike_trips_df['checkins'] < 0, 'checkins'] = 0
    bike_trips_df['checkins'] = bike_trips_df['checkins'].abs()

    # Might want to use sum of checkouts and checkins for find "busiest" stations
    bike_trips_df['totals'] = bike_trips_df['checkouts'] + bike_trips_df['checkins']
    
    return bike_trips_df

def load_daily_rentals():

    bike_trips_df = load_bike_trips()
    daily_bikes_df = bike_trips_df.copy()
    daily_bikes_df = daily_bikes_df.reset_index()
    daily_bikes_df = daily_bikes_df[['datetime', 'checkouts']]
    daily_bikes_df.columns = ['date', 'rentals']
    daily_bikes_df = daily_bikes_df.groupby('date').sum()
    daily_bikes_df = daily_bikes_df.resample('1D').sum()

    return daily_bikes_df
