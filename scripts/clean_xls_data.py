# Process HTML files to generate a csv of bikes at each station, and station locations


from os import listdir
from glob import glob
import re
import copy

import pandas as pd
from tqdm import tqdm
import os
import fnmatch
import sys

import numpy as np
import scipy as sp
import pandas as pd

XLS_DIR = '../data/AustinBcycleTripData'
OUT_FILE = '../input/all_trips.csv'

def find_excel_files(dir, filematch):
    '''Finds all Excel files under the given directory matching filename
    INPUT: dir - string with root directory to search recursively under
           filematch - string with file matching (Use '*' for none)
    RETURNS: List of matching files
    '''
    # print('Finding Excel files, dir {}, filematch {}'.format(dir, filematch))
    xls_files = list()

    # Find the files recursively
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, filematch):
            # print('root is {}'.format(root))
            # print('dirname is {}'.format(dirnames))
            # print('filename is {}'.format(filename))
            xls_file = root + '/' + filename
            xls_files.append(xls_file)
    return xls_files

def read_excel_files(xls_files):
    '''Reads in all the excel files a single pandas dataframe
    INPUT: List of filenames of Excel files
    RETURNS: Pandas dataframe with concatenated result
    '''

    xls_dfs = list()
    col_names = None

    for file in tqdm(xls_files, desc='Reading Excel files'):
        xls_df = pd.read_excel(file)
        xls_df.columns = xls_df.columns.str.strip()
        if col_names is None:
            col_names = xls_df.columns
        else:
            # Need to strip leading and trailing whitespace from column names for exact match
            assert col_names.equals(xls_df.columns), 'Error - column name mismatch in {}. \nExpected {}, \nActual {}'.\
                format(file, col_names, xls_df.columns)
        xls_dfs.append(xls_df)

    xls_df = pd.concat(xls_dfs, ignore_index=True)
    return xls_df





def main(argv=None):
    '''
    Function called to run main script including unit tests
    INPUT: List of arguments from the command line
    RETURNS: Exit code to be passed to sys.exit():
        -1: Invalid input
         0: Script completed successfully
    '''


    if argv is None:
        arg = sys.argv

    # Find all Excel files stored in directories under XLS_DIR
    # print('Finding Excel files...')
    excel_files = find_excel_files(XLS_DIR, 'TripReport-*.xlsx')
    # print('Found {} Excel files'.format(len(excel_files)))

    xls_df = read_excel_files(excel_files)
    xls_df = xls_df.sort_values('Checkout Date')
    print('Dataframe head():\n{}\n'.format(xls_df.head()))
    print('Dataframe null values:\n{}\n'.format(xls_df.isnull().sum(axis=0)))
    print('Dataframe info:\n{}'.format(xls_df.info()))

    xls_df.to_csv(OUT_FILE, index=False)

    # For each of the files, read in and create pandas dataframe
    # Combine all the pandas in together


if __name__ == '__main__':
    sys.exit(main())