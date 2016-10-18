##############################################################################
##
## Data Loading and cleaning
##
## Class: PCE Data Science Methods Class
##
## Please run from the project/scripts directory so relative paths work
##
##############################################################################

##############################################################################
# Clear objects from Memory
rm(list=ls())
# Clear Console:
cat("\014")

##############################################################################
# Libraries 
#
library(lubridate)
library(ggplot2)
library(assertthat)
library(logging)
library(GGally)
library(ggmap)


##############################################################################
# Helper function and tests 
#

# Creates a dataframe with year, month, and day columns from input date 
ymd_from_date <- function(dates) {
  
  ymd_data <- data.frame(year(dates), month(dates), day(dates))
  colnames(ymd_data) <- c('year', 'month', 'day')
  rownames(ymd_data) <- NULL
  return(ymd_data)
  
}

test_ymd_from_date <- function(tests = 100) {
  
  logdebug(paste("Testing ymd_from_date: ", tests, " times"))
  
  for (test in 1:tests) {
    
    year <- sample(1:2000, 1)
    month <- sample(1:12, 1)
    day <- sample(1:28, 1)
    date_string <- paste(year, month, day, sep = '-')
    date <- as.Date(strptime(date_string, format = "%Y-%m-%d"))
    
    logdebug(paste("Testing date ", date))
    
    ymd_data <- ymd_from_date(date)
    
    assert_that(ymd_data$year == year)
    assert_that(ymd_data$month == month)
    assert_that(ymd_data$day == day)
    logdebug(paste("Test ", test, " passed"))
  }
  
}


hms_from_time <- function(times) {
  
  hms_time <- data.frame(hour(times), minute(times), second(times))
  colnames(hms_time) <- c('hour', 'minute', 'second')
  rownames(hms_time) <- NULL
  return(hms_time)
}

test_hms_from_time <- function(tests = 100) {
  
  logdebug(paste("Testing hms_from_date: ", tests, " times"))
  
  for (test in 1:tests) {
    
    hour <- sample(0:23, 1)
    minute <- sample(0:59, 1)
    second <- sample(0:59, 1)
    time_string <- paste(hour, minute, second, sep = ':')
    time <- strptime(time_string, format = "%H:%M:%S")
    
    logdebug(paste("Testing time ", time))
    
    hms_data <- hms_from_time(time)
    
    assert_that(hms_data$hour == hour)
    assert_that(hms_data$minute == minute)
    assert_that(hms_data$second == second)
    logdebug(paste("Test ", test, " passed"))
  }
}


##############################################################################
# Function and unit-test declarations 
#

# -- Setup functions --

# Function to set up a logger to print out debugging information
init_logger <- function(log_file_stem, log_level, time_stamp = TRUE) {
  # Guard statements 
  assert_that(is.string(log_file_stem))
  assert_that(is.string(log_level))
  
  valid_log_levels <- c('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')
  assert_that(log_level %in% valid_log_levels)
  
  basicConfig()
  
  if (time_stamp) {
    date_time <- strftime(Sys.time(), format = "%Y-%m-%d_%H:%M:%S")
    log_file <- paste("~/", log_file_stem, "_", date_time, ".log", sep = "")
  } else {
    log_file <- paste("~/", log_file_stem, ".log", sep = "")
  }
  
  addHandler(writeToFile, file=log_file, level=log_level)
  return(log_file) # Return the log file, so it can be checked later
}

# -- Data loading functions --

# Load in the stations data
load_csv_data <- function(filename, col_check = NA, row_check = NA,
                          strings_as_factors = TRUE) {
  
  assert_that(file.exists(filename))
  data <- read.csv(filename, stringsAsFactors = strings_as_factors)
  
  # Optionally check the number of rows
  if (!is.na(row_check)) {
    assert_that(nrow(data) == row_check)
  }
  
  # Optionally check the number of columns
  if (!is.na(col_check)) {
    assert_that(ncol(data) == col_check)
  }
  
  return(data)
}


# Load in the stations data
load_station_data <- function(filename = '../data/stations.csv') {
  assert_that(file.exists(filename))
  data <- read.csv(filename)
}

# -- Data cleaning functions --

# Don't need any extra cleaning on the station data
clean_station_data <- function(data_in) {
  return(data_in)
}

# bike data needs reformatting to help plotting and model training.
clean_bike_data <- function(data_in) {
  
  # Use unique datetime values to create column
  data_out <- data.frame(unique(data_in$datetime))
  colnames(data_out) <- c('datetime')
  
  # Convert date and time to internal format, split out individual components
  data_out$datetime <- strptime(data_out$datetime, format = "%Y-%m-%d %H:%M:%S")
  ymd_data <- ymd_from_date(data_out$datetime)
  hms_data <- hms_from_time(data_out$datetime)
  data_out <- cbind(data_out, ymd_data, hms_data)
  data_out[, 'week_of_year'] <- week(data_out$datetime)
  data_out[, 'day_of_week'] <- wday(data_out$datetime, label = TRUE)
  data_out[, 'day_of_year'] <- yday(data_out$datetime)
  data_out$is_weekend <- (data_out$day_of_week == 'Sat') | (data_out$day_of_week == 'Sun')
  data_out$is_weekday <- !data_out$is_weekend
  data_out$day_of_year <- data_out$day_of_year - data_out$day_of_year[1] + 1
#   data_out$is_full <- data_out$avail == 0
#   data_out$is_empty <- data_out$bikes == 0
    
  # Instead of a long list of station_id and datetime values, create
  # a single row for each datetime, and bikes or availability along
  # the columns
  
  unique_station_ids <- 1:48
  num_samples <- sum(data_in$station_id == 1)
  station_diff_agg <- rep(0, num_samples)
  
  for (id in unique_station_ids) {
    logdebug(paste('Processing station ', id))
    station_count <- data_in$bikes[data_in$station_id == id]
    station_count_diff <- c(0, diff(station_count))
    station_count_diff[station_count_diff > 0] <- 0
    station_diff_agg <- station_diff_agg + station_count_diff
  }
  
  data_out$checkouts <- abs(station_diff_agg)

  return(data_out)
}


clean_weather_data <- function(data_in, trace_precipitation = 0.01) {
  
  data_out <- data_in
  
  # Change column names to easier strings
  colnames(data_out) <- c('date', 
                          'max_temp', 'mean_temp', 'min_temp',
                          'max_dew', 'mean_dew', 'min_dew', 
                          'max_humidity', 'mean_humidity', 'min_humidity',
                          'max_pressure', 'mean_pressure', 'min_pressure',
                          'max_visibility', 'mean_visibility', 'min_visibility',
                          'max_windspeed', 'mean_windspeed', 
                          'max_gustspeed', 'precipitation', 'cloud_cover',
                          'events', 'wind_dir')
  
  # Convert the date into a POSIX date, create year, month, date columns
  data_out$date <- strptime(data_out$date, format = "%Y-%m-%d")
  ymd_data <- ymd_from_date(data_out$date)
  data_out <- cbind(data_out, ymd_data)
  
  # The 'T' in the precipitation means a trace amount of precipitation.
  # replace this with a small amount so it can be treated as numeric
  data_out$precipitation <- as.numeric(data_out$precipitation) 
  data_out$precipitation[is.na(data_out$precipitation)] <- trace_precipitation
  
  # Cloud cover is an ordinal variable from 0 to 8 for increasing clouds
  data_out$cloud_cover <- as.ordered(data_out$cloud_cover)
  
  # Events are a combination with '-' separator of the following:
  # Rain, Thunderstorm, Fog, Hail. In any combination.
  # So convert this to onehot encoding here
  data_out$is_rain <- grepl('Rain', data_out$events)
  data_out$is_thunderstorm <- grepl('Thunderstorm', data_out$events)
  data_out$is_fog <- grepl('Fog', data_out$events)
  data_out$is_hail <- grepl('Hail', data_out$events)
  
  # The wind_dir has the HTML code for newline appended, e.g. 19<br />
  # So remove the <br /> from the end, convert to integer.
  # If there's no value, this returns -1, convert to NA.
  data_out$wind_dir <- sub('<br />', '', data_out$wind_dir) # todo ! Fix warnings
  data_out$wind_dir[is.na(data_out$wind_dir)] <- '-1'
  data_out$wind_dir <- as.numeric(data_out$wind_dir)
  data_out$wind_dir[data_out$wind_dir == -1] <- NA
  
  # Remove all the original fields that aren't needed
  data_out$events <- NULL
  
  return(data_out)
  
}

# Aggregates the checkouts by day and hour
graph_checkouts_by_time_and_day <- function(data_in) {
  bike_hourly_data <- aggregate(checkouts ~ day_of_week + hour, data = data_in, FUN = sum)
  p <- ggplot(bike_hourly_data, aes(x=hour, y=checkouts, color=day_of_week))
  p <- p + geom_smooth(se = FALSE, span = 0.1)
  p <- p + theme(legend.title=element_blank())
  p <- p + scale_x_continuous(breaks = seq(0,23))
  p <- p + scale_y_continuous(breaks = seq(0,800, 100))
  p <- p + xlab("Hour of the day")
  p <- p + ylab("Aggregated bike Checkouts") 
  p <- p + ggtitle("Bike checkouts by day and hour-of-day")
  p <- p + theme(plot.title = element_text(size=16))
  print(p)
  
  lm_model <- lm(checkouts ~ hour, data = data_in)
  summary(lm_model)
  
  return(lm_model)
}


# Check for correlation between checkouts and weather conditions
graph_correlation_checkouts_and_weather <- function(bike_data_in, weather_data_in) {
  
  bike_data <- aggregate(checkouts ~ year + month + day + hour + day_of_week, 
                               data = bike_data_in, FUN = sum)
  
  bike_data <- merge(bike_data, weather_data_in, 
                                    by = c('year', 'month', 'day'))
  
  p <- ggplot(bike_data, aes(x = max_windspeed, y = checkouts))
  p <- p + geom_point()
  p <- p + geom_jitter()
  p <- p + ggtitle("Jittered bike checkouts vs windspeed")
  p <- p + xlab("Maximum Windspeed (MPH)")
  p <- p + ylab("Number of checkouts")
  print(p)
  
  lm_model <- lm(checkouts ~ max_windspeed, data = bike_data)
  summary(lm_model)
  
  return(lm_model)
}


graph_checkouts_on_map <- function(bike_src_data_in, station_data_in) {
  
  data_in <- bike_src_data_in
  station_data <- station_data_in
  
  # format the bike data to show how many bike trips left from each station
  unique_station_ids <- 1:48
  station_df <- data.frame(unique_station_ids)
  num_samples <- sum(data_in$station_id == 1)
  station_diff_agg <- rep(0, num_samples)
  
  for (id in unique_station_ids) {
    logdebug(paste('Processing station ', id))
    station_count <- data_in$bikes[data_in$station_id == id]
    station_count_diff <- c(0, diff(station_count))
    station_count_diff[station_count_diff > 0] <- 0
    station_count <- sum(abs(station_count_diff))
    station_data[id, 'count'] <- station_count
  }
  
  
  gc <- geocode("Austin, TX")
  map <- get_map(gc, source = "google", maptype = "roadmap", zoom = 13)
  bb <- attr(map, "bb") # c(-97.80, 30.24, -97.70, 30.3) # 
  bbox <- bb2bbox(bb)
  
  p <- ggmap(map)
  p <- p + geom_point(aes(x = long, y = lat, size = count),
      data = station_data, colour = "red", alpha = 0.6)
  # p <- p + scale_size_area(range = c(3, 10000))
  p <- p + ggtitle("Bike checkouts by station")
  p <- p + xlab("")
  p <- p + ylab("")
  p <- p + theme(legend.title=element_blank())
  print(p)
}

##############################################################################
# Main interactive section
#

if (interactive()) {
  
  loginfo("Initialising logging")
  log_filename <- init_logger('tim_gasser_proj', 'DEBUG', time_stamp = TRUE)
  
  loginfo("Runnning unit tests")
  test_ymd_from_date()
  test_hms_from_time()
  
  
  
  loginfo("Reading in data") # todo ! Check the rows and columns are correct too
  station_src_data <- load_csv_data('../data/stations.csv', strings_as_factors = FALSE)
  bike_src_data <- load_csv_data('../data/bikes.csv', strings_as_factors = FALSE)
  weather_src_data <- load_csv_data('../data/weather.csv', strings_as_factors = FALSE)
  
  loginfo("Cleaning and re-formatting data")
  station_data <- clean_station_data(station_src_data)
  bike_data <- clean_bike_data(bike_src_data)
  weather_data <- clean_weather_data(weather_src_data)

  # Do a series of exploration plots, with linear models
  loginfo("Plotting bike checkouts by time of day and day of week")
  day_time_model <- graph_checkouts_by_time_and_day(bike_data)
  
  loginfo("Plotting correlation between weather variables and checkouts ")
  weather_model <- graph_correlation_checkouts_and_weather(bike_data, weather_data)
  
  loginfo("Plotting checkouts on map of Austin")
  graph_checkouts_on_map(bike_src_data, station_data)
  
  
}
