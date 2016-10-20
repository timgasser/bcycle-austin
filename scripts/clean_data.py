# Process HTML files to generate a csv of bikes at each station, and station locations


from os import listdir
from glob import glob
import re
import copy

import pandas as pd
from tqdm import tqdm

HTML_DIR = '../data/html'
DATA_DIR = '../data'

LAT_IDX = 0
LONG_IDX = 1

STAT_NAME = 0
STAT_ADDRESS = 1
STAT_BIKES = 2
STAT_AVAIL = 3

files = glob(HTML_DIR + '/*.html')
# num_files = len(files)
# print('Found {} files'.format(len(files)))

date_re = re.compile('.*stations_(\d{4}-\d{2}-\d{2}).*\.html')
time_re = re.compile('.*stations_\d{4}-\d{2}-\d{2}_(\d{2}:\d{2}:)\d{2}.*\.html')
station_re = re.compile('^var marker = new createMarker\(point, \"<div class=\'markerTitle\'><h3>(\w.*)</h3></div>\
<div class=\'markerPublicText\'><h5></h5></div>\
<div class=\'markerAddress\'>(\w.*)</div><div class=\'markerAvail\'>\
<div style=\'float: left; width: 50%\'><h3>(\d+)</h3>Bikes</div>\
<div style=\'float: left; width: 50%\'><h3>(\d+)</h3>Docks</div></div>\"')
latlong_re = re.compile('var point = new google\.maps\.LatLng\((.+), (.+)\);')

# Dictionary to store stations (fast lookup by lat/lon)
stations = dict()

# List to store the bike values for each station in a series
bike_list = list()


file_counter = 0
verbose = False
short_run = False

for bike_idx, bike_filename in tqdm(enumerate(files),  total=len(files)):
    file_counter += 1
    if short_run and (file_counter == 10):
        break

    date = str(date_re.match(bike_filename).groups(0)[0])
    time = str(time_re.match(bike_filename).groups(0)[0])
    time += '00'
    datetime_string = date + ' ' + time

    with open(bike_filename, 'r') as bike_file:
        for line in bike_file:
            # print line
            # Check for latitude and longitude
            match = latlong_re.match(line)
            if (match != None):
                latitude = float(latlong_re.match(line).groups()[LAT_IDX])
                longitude = float(latlong_re.match(line).groups()[LONG_IDX])
                latlon = (latitude, longitude)
                if verbose:
                    print('Found lat {}, lon {}'.format(latitude, longitude))

            match = station_re.match(line)
            if (match != None):

                name = str(station_re.match(line).groups()[STAT_NAME])
                address = station_re.match(line).groups()[STAT_ADDRESS].replace('<br />', ', ')
                address.replace('<br />', ', ')
                bikes = int(station_re.match(line).groups()[STAT_BIKES])
                avail = int(station_re.match(line).groups()[STAT_AVAIL])

                if (latlon not in stations):
                    new_station = dict()
                    new_station['name'] = name
                    new_station['address'] = address
                    new_station['lat'] = latitude
                    new_station['long'] = longitude
                    new_station['date'] = date
                    new_station['time'] = time
                    stations[latlon] = new_station

                    if verbose:
                        print('Adding new station: {}'.format(new_station))

                new_bike = dict()
                new_bike['latlon'] = latlon
                new_bike['datetime'] = datetime_string
                new_bike['bikes'] = bikes
                new_bike['avail'] = avail
                bike_list.append(new_bike)
                if verbose:
                    print('Lat = {}, lon = {}, bikes = {}, avail = {}'.format(latitude, longitude, bikes, avail))
                # print 'Found {} stations'.format(len(station_list))


print('Found {} stations'.format(len(stations)))
print('Found records from {} to {}'.format(bike_list[0]['datetime'], bike_list[-1]['datetime']))

# print('Converting station and bike data to csv file')
#
# # Convert to pandas dataframes
# # stations_inv_dict = {v: k for k, v in stations_dict.items()}
# # stations_df = pd.DataFrame(station_list)
# # stations_df = stations_df[['station_id', 'name', 'address', 'lat', 'long', 'capacity']]
#
# bikes_df = pd.DataFrame(bike_list)
# # bikes_df = bikes_df[['station_id', 'datetime', 'bikes', 'avail']]
#
# # print('Stations dataframe')
# # print(stations_df)
# print('Bikes dataframe')
# print(bikes_df)
#
# stations_df.to_csv(DATA_DIR + '/stations.csv', index=False)
# bikes_df.to_csv(DATA_DIR + '/bikes.csv', index=False)
