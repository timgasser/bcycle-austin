# Austin BCycle Analysis

This github repo contains all the code used in the BCycle analysis. The raw data is too large to host on github, and is stored in a Dropbox link for download. 

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
