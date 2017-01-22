# Austin BCycle Analysis

This github repo contains all the code and data used in the 3-part BCycle analysis posted on Medium. To read the posts, click on the links below.

* [Analyzing BCycle Stations](https://austinstartups.com/analyzing-austin-bcycle-rentals-stations-d9a1863d17e9#.ytrns0u09)
* [Analyzing BCycle Rentals](https://austinstartups.com/analyzing-austin-bcycle-rentals-34e52424858a#.4jtsq6yz2) 
* [Machine Learning with Austin BCycle](https://austinstartups.com/machine-learning-with-austin-bcycle-55f90456e72c#.pll2et6xt)

## Directory hierarchy

* `data` - Contains shell script to download and untar the raw HTML from my Dropbox area.
* `input` - Contains CSV files generated by processing the raw HTML files in the `data` directory.
* `notebooks` - Notebooks used to analyze the data, produce plots, and explain the trends seen.
* `scripts` - Scripts used to generate CSV files in `input` directory from the raw HTML in `data`.

## Environment Setup

I'm using the [Anaconda Python](https://www.continuum.io) distribution. This is a great all-in-one distribution which sets up all the Python packages, Jupyter notebooks, and command-line interfaces you need.

If you're using Anaconda, I also saved out an environment file. This contains all the packages you need to run the notebooks. To create the environment, run the command below.

```
$ conda env create -f bcycle_env.yml
```

## Quickstart Guide

The CSV files in the `input` directory have been checked into git, so once you clone the repo you can extract them and start running notebooks, and your own analysis.

To uncompress the CSV files, use the following commands:

```
$ cd input
$ unzip '*.zip'
Archive:  bikes.csv.zip
  inflating: bikes.csv               

Archive:  stations.csv.zip
  inflating: stations.csv            

2 archives were successfully processed.
```

The contents of the `input` directory should now be:

```
$ ls -l
total 49896
-rw-r--r--  1 tim  staff    22M Oct 20 20:32 bikes.csv
-rw-r--r--  1 tim  staff   2.5M Nov 12 17:39 bikes.csv.zip
-rw-r--r--  1 tim  staff   5.2K Oct 20 20:32 stations.csv
-rw-r--r--  1 tim  staff   1.8K Nov 12 17:39 stations.csv.zip
```

Now the CSV files are ready, open up any of the notebooks in the `notebooks` subdirectory and you should be good to go !


## Full Guide

If you'd like to run all the steps of the data pipeline, follow the steps below.

### Downloading raw HTML

To download the raw HTML, you can run the shell script below. This downloads the zipped tarball from my Dropbox area, and unzips into an html subdirectory.

```
$ cd data
$ ./get_data.sh
```

You should see the file being downloaded, and then HTML files unzipping into the html subdirectory.

### Converting HTML to CSV files

This step uses the `clean_data.py` script in the `scripts` subdirectory to process the HTML files. The input files are all taken from `data`, and written out to `input`.

To do the conversion, follow the instructions below. The script uses the `tqdm` package to show a progress bar as the HTML files are converted.

```
$ cd scripts
$ python clean_data.py 
 20%|███████▌                             | 3562/17504 [00:14<00:53, 260.78it/s]

```

Once this completes, all the CSV files will be ready to go in the `input` directory.


### Notebooks

The notebooks are split into those which use the 2-months of data I scraped, and the ones that use the full 3-year dataset from AUstin BCycle. The ones using the full dataset have `bcycle_all_data` in their title. The others run with the csv files supplied in zip format in Git.

#### April/May 2016 notebooks

Please make sure you unzip the zip files in the `input` directory before running these notebooks.

* `bcycle_stations.ipynb` - Analysis of BCycle stations, looking at which aren't full or empty 90% of the time.

* `bcycle_bikes.ipynb` - Analysis of bike trips leaving and arriving at  stations.

* `bcycle_weather.ipynb` - Plots of weather during April and May 2016 in Austin.

* `bcycle_hourly_rental_models.ipynb` - Machine learning models predicting hourly rentals.

#### Full data notebooks

The data needed for these notebooks has to be requested from Austin BCycle. You can still browse these, and see the results though.

* `bcycle_all_data_clean.ipynb` - Notebook to clean the raw BCycle data. Includes:
    * Removing stations which are only found in checkout or checkin column.
    * Removing non-numeric bike IDs in the `bike_id` field.
    * Geocoding stations whose locations aren't available on the current website.
    
* `bcycle_all_data_eda.ipynb` - Exploratory data analysis on the full data.

* `bcycle_all_data_models.ipynb` - Machine learning models to predict hourly rentals using the full 3 year dataset.


