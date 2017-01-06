# Common library routines for the BCycle analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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



