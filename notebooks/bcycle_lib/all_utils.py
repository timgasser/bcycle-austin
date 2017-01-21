# Common library routines for the BCycle analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# sklearn section
from sklearn.preprocessing import LabelBinarizer, MinMaxScaler, scale



INPUT_DIR = '../input'

# All-data utilities

def col_convert(df, col, new_type, verbose=False):
    '''Convert the column to the new type, after doing some asserts'''

    # Don't do any range checking on floats
    if new_type in (np.float16, np.float32, np.float64):
        df[col] = df[col].astype(new_type) # Convert the type and return dataframe
        return df[col]

    # Range-check the integers
    type_info = np.iinfo(new_type) # Find out min and max val of new type
    max_val = type_info.max
    min_val = type_info.min
    
    if verbose:
        print('Type: {}, min {}, max {}'.format(new_type, min_val, max_val))
        print('DF: min {}, max {}'.format(df[col].min(), df[col].max()))
        
    assert df[col].max() <= max_val, '{} max is {}, new type max {}'.format(col, df[col].max(), max_val)
    assert df[col].min() >= min_val, '{} min is {}, new type min {}'.format(col, df[col].min(), min_val)

    df[col] = df[col].astype(new_type) # Convert the type and return dataframe
    return df[col]
    
def clean_bcycle_types(stations_df, trips_df, verbose=False):
    '''Converts the column types to proper values'''
    # Convert column types to appropriate values
    if verbose:
        print('Converting Station table types')
        
    stations_df['station_id'] = col_convert(stations_df, 'station_id', np.uint8, verbose)
    stations_df['lat'] = col_convert(stations_df, 'lat', np.float32, verbose)
    stations_df['lon'] = col_convert(stations_df, 'lon', np.float32, verbose)

    if verbose:
        print('Converting Bike table types')
        
    trips_df['datetime'] = pd.to_datetime(trips_df['datetime'])
    trips_df['membership'] = trips_df['membership'].astype('category')
    trips_df['bike_id'] = col_convert(trips_df, 'bike_id', np.uint16, verbose)
    trips_df['checkout_id'] = col_convert(trips_df, 'checkout_id', np.uint8, verbose)
    trips_df['checkin_id'] = col_convert(trips_df, 'checkin_id', np.uint8, verbose)
    trips_df['duration'] = col_convert(trips_df, 'duration', np.uint16, verbose)
    trips_df = trips_df.set_index('datetime', drop=True)
    return stations_df, trips_df

def load_bcycle_data(directory, station_filename, trips_filename, verbose=False):  
    '''Loads cleaned station and trips files
    INPUT: directory - string containing directory with files
           station_filename - stations table CSV file
           trips_filename - trips table CSV file
           verbose - print out extra information after loading
    RETURNS: Tuple with (stations, trips) dataframes
    '''
    
    stations_df = pd.read_csv(directory + '/' + station_filename)
    trips_df = pd.read_csv(directory + '/' + trips_filename)

    stations_df, trips_df = clean_bcycle_types(stations_df, trips_df, verbose)
    
    if verbose:
        print('\nStations shape:\n{}'.format(stations_df.shape))
        print('\nStations info:\n{}'.format(stations_df.info()))
        print('\nStations stats:\n{}'.format(stations_df.describe()))

        print('\n ------ \n')


        print('\nTrips shape:\n{}'.format(trips_df.shape))
        print('\nTrips shape:\n{}'.format(trips_df.info()))
        print('\nTrips stats:\n{}'.format(trips_df.describe()))

    return (stations_df, trips_df)


def clean_weather(df):
    '''Cleans weather dataframe'''

    # Remove whitespace and keep min/max values
    df.columns = [col.strip() for col in df.columns]
    date_col = df.columns[0]
    df = df[[date_col,'Max TemperatureF','Min TemperatureF', 
             'Max Humidity', 'Min Humidity',
             'Max Sea Level PressureIn', 'Min Sea Level PressureIn', 
             'Max Wind SpeedMPH', 'Mean Wind SpeedMPH', 'Max Gust SpeedMPH',
             'PrecipitationIn', 'CloudCover', 'Events']]
    
    # Clean up column names, drop means as they're a linear combination of max/min
    df.columns = ['date', 'max_temp', 'min_temp', 'max_humidity', 'min_humidity',
                 'max_pressure', 'min_pressure', 'max_wind', 'min_wind', 'max_gust',
                 'precipitation', 'cloud_cover', 'events']
    
    # Convert column types appropriately
    df.loc[:,'date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')  
    df = df.set_index('date', drop=True)
    
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
        df[event] = df['events'].apply(str.lower).str.contains(event).astype(np.uint8)
    
    df = df.drop(['events', 'none'], axis=1)
    return df




# Plotting functions

def plot_lines(df, subplots, title, xlabel, ylabel):
    '''Generates one or more line plots from pandas dataframe'''
    
    fig, ax = subplots
    ax = df.plot.line(ax=ax)
    ax.set_xlabel(xlabel, fontdict={'size' : 14})
    ax.set_ylabel(ylabel, fontdict={'size' : 14})
    ax.set_title(title, fontdict={'size' : 18}) 
    ttl = ax.title
    ttl.set_position([.5, 1.02])
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)   

    
def plot_boxplot(df, order, x, y, figsize, title, xlabel, ylabel):
    '''Plots a boxplot using given '''
    fig, ax = plt.subplots(1,1, figsize=figsize)  
    ax = sns.boxplot(data=df, x=x, y=y, order=order)
    ax.set_xlabel(xlabel, fontdict={'size' : 14})
    ax.set_ylabel(ylabel, fontdict={'size' : 14})
    ax.set_title(title, fontdict={'size' : 18})
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ttl = ax.title
    ttl.set_position([.5, 1.02])


def plot_bar(df, size, title, xlabel, ylabel):
    '''Plots a bar graph of the dataframe '''
    
    palette = sns.color_palette('Set2', len(df.columns)) # Don't repeat colours
    fig, ax = plt.subplots(1, 1, figsize=size)
    ax = df.plot.bar(ax=ax, color=palette, rot=0)
    ax.set_xlabel(xlabel, fontdict={'size' : 14})
    ax.set_ylabel(ylabel, fontdict={'size' : 14})
    ax.set_title(title, fontdict={'size' : 18}) 
    ttl = ax.title
    ttl.set_position([.5, 1.02])
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)   
    ax.legend(fontsize = 14)


def plot_hist(df_col, bins, size, title, xlabel, ylabel):
    '''Plots a histogram of the dataframe column'''
    
    fig, ax = plt.subplots(1, 1, figsize=size)
    ax = df_col.plot.hist(ax=ax, bins=bins)
    ax.set_xlabel(xlabel, fontdict={'size' : 14})
    ax.set_ylabel(ylabel, fontdict={'size' : 14})
    ax.set_title(title, fontdict={'size' : 18}) 
    ttl = ax.title
    ttl.set_position([.5, 1.02])
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)   


# Model evaluation plotting functions

def df_from_results(index_train, y_train, y_train_pred, index_val, y_val, y_val_pred):
    '''Creates dataframe from results for use in plotting functions below'''
    train_dict = dict()
    val_dict = dict()

    train_dict['true'] = y_train
    train_dict['pred'] = y_train_pred

    val_dict['true'] = y_val
    val_dict['pred'] = y_val_pred

    train_df = pd.DataFrame(train_dict)
    val_df = pd.DataFrame(val_dict)

    train_df.index = index_train
    val_df.index = index_val
    
    return train_df, val_df
    
   

def plot_val(val_df, pred_col, true_col, title):
    '''
    Plots the validation prediction
    INPUT: val_df - Validation dataframe
           pred_col - string with prediction column name
           true_col - string with actual column name
           title - Prefix for the plot titles.
    RETURNS: Nothing
    '''
    def plot_ts(df, pred, true, title, ax):
        '''Generates one of the subplots to show time series'''
        ax = df.plot(y=[true, pred], ax=ax) # , color='black', style=['--', '-'])
        ax.set_xlabel('Date', fontdict={'size' : 14})
        ax.set_ylabel('Rentals', fontdict={'size' : 14})
        ax.set_title(title, fontdict={'size' : 16}) 
        ttl = ax.title
        ttl.set_position([.5, 1.02])
        ax.legend(['Predicted rentals', 'Actual rentals'], fontsize=14, loc=2)
        ax.tick_params(axis='x', labelsize=14)
        ax.tick_params(axis='y', labelsize=14)
    
    fig, ax = plt.subplots(1,1, sharey=True, figsize=(16,8))
    plot_ts(val_df, pred_col, true_col, title + ' (validation set)', ax)
    

def plot_prediction(train_df, val_df, pred_col, true_col, title):
    '''
    Plots the predicted rentals along with actual rentals for the dataframe
    INPUT: train_df, val_df - pandas dataframe with training and validataion results
           pred_col - string with prediction column name
           true_col - string with actual column name
           title - Prefix for the plot titles.
    RETURNS: Nothing
    '''
    def plot_ts(df, pred, true, title, ax):
        '''Generates one of the subplots to show time series'''
        plot_df = df.resample('1D').sum()
        ax = plot_df.plot(y=[pred, true], ax=ax) # , color='black', style=['--', '-'])
        ax.set_xlabel('', fontdict={'size' : 14})
        ax.set_ylabel('Rentals', fontdict={'size' : 14})
        ax.set_title(title, fontdict={'size' : 16}) 
        ttl = ax.title
        ttl.set_position([.5, 1.02])
        ax.legend(['Predicted rentals', 'Actual rentals'], fontsize=14)
        ax.tick_params(axis='x', labelsize=14)
        ax.tick_params(axis='y', labelsize=14)   
    
    fig, axes = plt.subplots(2,1, sharey=True, figsize=(20,12))
    plot_ts(train_df, pred_col, true_col, title + ' (training set)', axes[0])
    plot_ts(val_df, pred_col, true_col, title + ' (validation set)', axes[1])
    
def plot_residuals(train_df, val_df, pred_col, true_col, title):
    '''
    Plots the residual errors in histogram (between actual and prediction)
    INPUT: train_df, val_df - pandas dataframe with training and validataion results
           pred_col - string with prediction column name
           true_col - string with actual column name
           title - Prefix for the plot titles.
    RETURNS: Nothing

    '''
    def plot_res(df, pred, true, title, ax):
        '''Generates one of the subplots to show time series'''
        residuals = df[pred] - df[true]
        ax = residuals.plot.hist(ax=ax, bins=20)
        ax.set_xlabel('Residual errors', fontdict={'size' : 14})
        ax.set_ylabel('Count', fontdict={'size' : 14})
        ax.set_title(title, fontdict={'size' : 16}) 
        ttl = ax.title
        ttl.set_position([.5, 1.02])
        ax.tick_params(axis='x', labelsize=14)
        ax.tick_params(axis='y', labelsize=14)   
    
    fig, axes = plt.subplots(1,2, sharey=True, sharex=True, figsize=(20,6))
    plot_res(train_df, pred_col, true_col, title + ' residuals (training set)', axes[0])
    plot_res(val_df, pred_col, true_col, title + ' residuals (validation set)', axes[1])
    
    
def plot_results(train_df, val_df, pred_col, true_col, title):
    '''Plots time-series predictions and residuals'''
    plot_prediction(train_df, val_df, pred_col, true_col, title=title)
    plot_residuals(train_df, val_df, pred_col, true_col, title=title)
    
def plot_scores(df, title, sort_col=None):
    '''Plots model scores in a horizontal bar chart
    INPUT: df - dataframe containing train_rmse and val_rmse columns
           sort_col - Column to sort bars on
    RETURNS: Nothing
    '''
    fig, ax = plt.subplots(1,1, figsize=(12,8)) 
    if sort_col is not None:
        scores_df.sort_values(sort_col).plot.barh(ax=ax)
    else:
        scores_df.sort_values(sort_col).plot.barh(ax=ax)

    ax.set_xlabel('RMSE', fontdict={'size' : 14})
    ax.set_title(title, fontdict={'size' : 18}) 
    ttl = ax.title
    ttl.set_position([.5, 1.02])
    ax.legend(['Train RMSE', 'Validation RMSE'], fontsize=14, loc=0)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)


    
# Model training functions

def reg_x_y_split(df, target_col, target_func=None, ohe_cols=None, z_norm_cols=None, minmax_norm_cols=None):
    ''' Returns X and y to train regressor
    INPUT: df = Dataframe to be converted to numpy arrays 
           target_col = Column name of the target variable
           ohe_col = Categorical columns to be converted to one-hot-encoding
           z_norm_col = Columns to be z-normalized
    RETURNS: Tuple with X, y, df
    '''
    
    # Create a copy, remove index and date fields
    df_out = df.copy()
    df_X = df.copy()
    df_X = df_X.reset_index(drop=True)
    X = None
    
    # Convert categorical columns to one-hot encoding
    if ohe_cols is not None:
        for col in ohe_cols:
            print('Binarizing column {}'.format(col))
            lbe = LabelBinarizer()
            ohe_out = lbe.fit_transform(df_X[col])
            if X is None:
                X = ohe_out
            else:
                X = np.hstack((X, ohe_out))
            df_X = df_X.drop(col, axis=1)
            
    # Z-normalize relevant columns
    if z_norm_cols is not None:
        for col in z_norm_cols:
            print('Z-Normalizing column {}'.format(col))
            scaled_col = scale(df[col].astype(np.float64))
            scaled_col = scaled_col[:,np.newaxis]
            df_out[col] = scaled_col
            if X is None:
                X = scaled_col
            if X is not None:
                X = np.hstack((X, scaled_col))
            df_X = df_X.drop(col, axis=1)

    if minmax_norm_cols is not None:
        for col in minmax_norm_cols:
            print('Min-max scaling column {}'.format(col))
            mms = MinMaxScaler()
            mms_col = mms.fit_transform(df_X[col])
            mms_col = mms_col[:, np.newaxis]
            df_out[col] = mms_col
            if X is None:
                X = mms_col
            else:
                X = np.hstack((X, mms_col))
            df_X = df_X.drop(col, axis=1)

    # Combine raw pandas Dataframe with encoded / normalized np arrays
    if X is not None:
        X = np.hstack((X, df_X.drop(target_col, axis=1).values))
    else:
        X = df_X.drop(target_col, axis=1)
        
    y = df[target_col].values

    if target_func is not None:
        y = target_func(y)
    
    return X, y, df_out


def add_time_features(df):
    ''' Extracts dayofweek and hour fields from index
    INPUT: Dataframe to extract fields from
    RETURNS: Dataframe with dayofweek and hour columns
    
    '''
    df.loc[:,'dayofweek'] = df.index.dayofweek
    df.loc[:,'hour'] = df.index.hour
    df.loc[:,'day-hour'] = df.loc[:,'dayofweek'].astype(str) + '-' + df.loc[:,'hour'].astype(str)
    df = df.drop(['dayofweek', 'hour'], axis=1)
#    df.loc[:,'weekday'] = (df['dayofweek'] < 5).astype(np.uint8)
#    df.loc[:,'weekend'] = (df['dayofweek'] >= 5).astype(np.uint8)
    return df
