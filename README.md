# Austin BCycle Analysis

This github repo contains all the code used in the BCycle analysis. The raw data is too large to host on github, and is stored in a Dropbox link for download. 

## Raw data
The raw data is a 290MB tgz file containing all the page fetches performed every 5 minutes during April and May 2016 from the [Austin BCycle Stations](https://austin.bcycle.com/stations/station-locations) page. The tgz file contains 17507 files, which are named: `stations_YYYY-MM-DD_HH:MM:SS.html`. The filename provides the date and timestamp the file was downloaded, and the file contains raw HTML. No processing has been done on these files after the initial curl download of the page, as I wanted to have all the information for the pre-processing script.

### Raw data format
Each webpage fetch contains all the station information and how many bikes and docks are available at each of the stations. We can extract these from the JavaScript used to create markers on the Google Map. An example is shown below, split by `div` for the `var marker`.

```js
var icon = '/Controls/StationLocationsMap/Images/marker-active.png';
var back = 'markerAvailable';
var point = new google.maps.LatLng(30.26483, -97.73900);
kioskpoints.push(point);
var marker = new createMarker(point, 
"<div class='markerTitle'><h3>Convention Center / 4th St. @ MetroRail</h3></div>
<div class='markerPublicText'><h5>Station south of MetroRail Platform</h5></div>
<div class='markerAddress'>499 E. 4th St<br />Austin, TX 78701</div>
<div class='markerAvail'><div style='float: left; width: 50%'>
<h3>13</h3>Bikes</div><div style='float: left; width: 50%'>
<h3>4</h3>Docks</div></div>", 
icon, back, false);
```

From this we can extract:

* `var icon` Status of the station. The website lists 5 statuses as below:
    1. Active `marker-active.png`
    2. Special Event `marker-specialevent.png`
    3. Partial Service `marker-partialservice.png`
    4. Unavailable `marker-unavailable.png`
    5. Coming Soon `marker-comingsoon.png`
* `var point` Latitude and longitude of the station.
* `var marker` 
    * `markerTitle` Title of the station
    * `markerAddress` Address of the station
    * `markerAvail` Available Bikes and Docks.
       
### Extracting stations
As each of the files lists all of the stations with the amount of bikes and docks available, we have to split out the stations and their fixed values (location, name, and address). Then these can be stored in one table.

In a second table, we can then store the time series data of available bikes and docks for each of the stations, and link to the station table with a unique ID.

I originally assumed that the capacity (number of bikes + number of docks) was fixed for each of the stations, but after checking the data the capacity increased and decreased by 1 infrequently. I suspect this might be the case when a customer returns a bike and marks it as needing repair. In this case the returned bike doesn't increase the bike number, and the number of docks remains the same.

I also found out that some new stations opened during April and May ! There is a date field which shows the first date the station was seen in the page fetches. 









## Directory structure

The directories follow the structure below:

* `data` - This directory contains all the data used for the project, in a csv format.
* `data/html` - This directory contains the raw HTML files which were scraped from the Austin BCycle website.
* `docs` - The Word and PDF files for the final project write-up are here.
* `scripts` - This directory contains Python and R scripts used to clean and analyze the data.

## Data pipeline

The data pipeline is listed below, showing the size of the data, how it can be downloaded (if necessary), and which script process it to pass it onto the next stage.

* `data/html` - 1.5GB of HTML files scraped from the BCycle website (~300MB compressed). This data is too large to be stored on Canvas, and has to be downloaded from a Dropbox shared folder.
* `scripts/process_data` - This is a Python script which parses  the raw HTML in `data/html` into `data/stations.csv` and `data/bikes.csv`. These files are 5kB and 21MB respectively.
* `scripts/process_data.R` - This is an R script which loads in `data/stations.csv`, `data/bikes.csv` and `data/weather.csv`. It cleans and re-formats the data, merges data tables, and generates visualizations and statistical models to test hypotheses.
* `docs/TimGasserProject.{pdf, docx}` - This is the project write-up, in both Word and PDF format.

## Setup instructions

Before running any scripts, the raw HTML files scraped from the Austin BCycle website have to be downloaded to `data/html`. I create a shortlink to access the tar-gzipped files: [http://bit.ly/1UdQWAx](http://bit.ly/1UdQWAx)

To download the file using curl, you can follow the steps below. Alternatively, you can copy and paste the bitly link into a web browser, and save the file into the `data` directory. After following the steps below, you should have a `data/html` directory with 17504 files in it.

```
$ cd data
$ curl -L -o stations.html.tgz http://bit.ly/1UdQWAx
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   151  100   151    0     0    958      0 --:--:-- --:--:-- --:--:--   955
  0     0    0     0    0     0      0      0 --:--:--  0:00:01 --:--:--     0
100  289M  100  289M    0     0  4106k      0  0:01:12  0:01:12 --:--:-- 6335k
$ tar zxf stations.html.tgz 
$ rm stations.html.tgz
```

## Running the scripts

### clean_data.py

The first step is to transform the scraped data in `data/html` into `data/bikes.csv` and `data/stations.csv`. To do this, cd into the `scripts` directory, and run `clean_data.py`. This script takes a couple of minutes on my laptop and gives a running count of how many files it has processed.

Once the script finishes, check in the `data` directory to make sure `stations.csv` and `bikes.csv` have been created. These files are read in by the `process_data.R` script.

### process_data.R 

Now the csv files have been created, they can be loaded into RStudio and processed. Set the working directory as `scripts`, and run this `process_data.R`. You should see logging files created with a date and timestamp in your home directory, and linear models and visualizations being created.

## Project write-up

The Word and PDF versions of the final write-up can be found in the `docs` directory.
