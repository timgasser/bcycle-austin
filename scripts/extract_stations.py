# Read through all the HTML page fetches, extract the stations and their information


from glob import glob
import re
from tqdm import tqdm
import pandas as pd


HTML_DIR = '../data/html'
DATA_DIR = '../data'

LAT_IDX = 0
LONG_IDX = 1

STAT_NAME = 0
STAT_ADDRESS = 1
STAT_BIKES = 2
STAT_AVAIL = 3

files = glob(HTML_DIR + '/*.html')
num_files = len(files)

print('Found {} files'.format(len(files)))

date_re = re.compile('.*stations_(\d{4}-\d{2}-\d{2}).*\.html')
time_re = re.compile('.*stations_\d{4}-\d{2}-\d{2}_(\d{2}:\d{2}:)\d{2}.*\.html')
station_re = re.compile('^var marker = new createMarker\(point, \"<div class=\'markerTitle\'><h3>(\w.*)</h3></div>\
<div class=\'markerPublicText\'><h5></h5></div>\
<div class=\'markerAddress\'>(\w.*)</div><div class=\'markerAvail\'>\
<div style=\'float: left; width: 50%\'><h3>(\d+)</h3>Bikes</div>\
<div style=\'float: left; width: 50%\'><h3>(\d+)</h3>Docks</div></div>\"')
latlong_re = re.compile('var point = new google\.maps\.LatLng\((.+), (.+)\);')


class station(object):
    '''
    Station class is used to store the details of stations:
    - lat: latitude of the station
    - lon: longitude of the station
    - name: Name of the station (shown in large red text at top of marker)
    - address: Address of the station, or sponsor name
    - date: The first date the station was seen in the data

    NOTE: No capacity information is stored in the station table, as the capacity
    seems to change by 1 in both directions, often hour to hour
    '''
    def __init__(self, station_id, lat, lon, name, address, capacity, date, time):
        self.id = station_id
        self.lat = lat
        self.lon = lon
        self.name = name
        self.address = address
        self.capacity = capacity
        self.date = date
        self.time = time

    def __str__(self):
        # print_str = 'Station at lat {}, lon {}, name {}, address {}, capacity {}, date {}'.\
        #     format(self.lat, self.lon, self.name, self.address, self.capacity, self.date)
        # return print_str
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return

    def get_lat_lon(self):
        return self.lat, self.lon


# Create a dictionary to hold the stations. Key = name, Value = address
stations = dict()
station_counter = 0
file_station_count = 0

station_id = 0

for bike_idx, bike_filename in tqdm(enumerate(files),  total=len(files)):
    # print('Processing {} of {} files'.format(bike_idx, num_files))
    station_counter += 1
    if (station_counter == 10):
        break

    date = str(date_re.match(bike_filename).groups(0)[0])
    time = str(time_re.match(bike_filename).groups(0)[0])
    time += '00'
    datetime_string = date + ' ' + time

    with open(bike_filename, 'r') as bike_file:
        file_station_count = 0

        for line in bike_file:
            # print line
            # Check for latitude and longitude
            match = latlong_re.match(line)
            if match is not None:
                # print('Found lat and long !')
                lat = latlong_re.match(line).groups()[LAT_IDX]
                lon = latlong_re.match(line).groups()[LONG_IDX]
                pos_tuple = (lat, lon)
                file_station_count += 1

            match = station_re.match(line)
            if match is not None:
                # print('Found station !')

                name = str(station_re.match(line).groups()[STAT_NAME])
                address = station_re.match(line).groups()[STAT_ADDRESS].replace('<br />', ', ')
                bikes = int(station_re.match(line).groups()[STAT_BIKES])
                avail = int(station_re.match(line).groups()[STAT_AVAIL])
                total = bikes + avail

                new_station = station(station_id, lat, lon, name, address, total, date, time)
                if pos_tuple not in stations:
                    print('Date {}, Time {}'.format(date, time))
                    print('Adding new station {}'.format(new_station.name))
                    stations[pos_tuple] = new_station
                    station_id += 1
                else:
                    old_station = stations[pos_tuple]
                    assert new_station.name == old_station.name, print(new_station.name, old_station.name)
                    assert new_station.address == old_station.address, print(new_station.name, old_station.name)
                    # if new_station.capacity != old_station.capacity:
                    #     # print('Date {}, Time {}'.format(date, time))
                    #     # print('Station {} capacity change from {} to {}'.format(new_station.name,
                    #     #                                                         old_station.capacity,
                    #     #                                                         new_station.capacity))
                    #     stations[pos_tuple] = new_station

        # print('Found {} stations in file {}'.format(file_station_count, bike_filename))

print('Found {} stations'.format(station_counter))
[print(stations[station]) for station in stations]


stations_df = pd.DataFrame.from_dict(stations.__dict__, orient='index')
stations_df.show()
