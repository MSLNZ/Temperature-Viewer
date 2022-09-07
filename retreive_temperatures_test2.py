"""
5/5/14

given a list of temperatures and a folder
search that folder for all temperature files and produce a table of
interpolated temperatures
"""

import sys
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
#sys.path.append(r'L:\CMM Leitz\Ballplate_MSL\Python_analysis' )
#sys.path.append(r'C:\Users\e.howick\Documents\_Projects\General')
import pandas as pd
import numpy as np

#file names before 2013-09-01
tmpfiles_01 = ['x_Air.txt']
tmpfiles_01 = ['Mobile.txt']

#file names after 2013-09-01
tmpfiles_02 = ['x_Air.txt']

#for 2013 the month directories are 2013-05
#for 2014 the month directories are 2014-5

from datetime import datetime



def timeTMD(temp):
    """
    date parser to be used by pd.read_csv
    used for files wriiten by C# Temperature Monitor program
    convert 8/06/2012 11:08:05 a.m. to seconds since the epoch
    also convert 8/06/2012 11:08:05 am
    """
    dt = pd.NaT
    if temp:
        if type(temp) == str :
            date, tim, apm = temp.split()

            day, month, year = date.split('/')
            h, m, s = tim.split(':')
            if apm[0] == 'a' and int(h) == 12:
               h = 0
            if apm[0] == 'p' and int(h) !=12:
               h = int(h) + 12
            tt = [int(year), int(month), int(day), int(h), int(m), int(s), 0]
            dt = pd.datetime(*tt)
    if dt == pd.NaT:
        print('NA', temp)
    return dt


def retreive_temperatures_df_fixed(df, folder, file_list, date_col=None):
    """
    df          is a dataframe with an index of datetimes
    folder      is a string pointing to the correct month directory of files written by the
                temperature monitoring program
    file_list   list of filenames to examine for temperatures

    date_col    column to use for datetimes if date_col=None uses index

    returns df with an extra column of temperatures added for each file in file_list

    """

    if type(date_col) == int:
        datetimes = df.iloc[:,date_col].copy()
    else:
        datetimes = df.index

    print(df.count())
    print('len', len(datetimes))

    #interpolate temperatures
    for fn in file_list:
        fname = os.path.join(folder,fn)
        dfT = pd.read_csv(fname,sep=',',skiprows=2,
                         names=('temp','channel','datetime','room','location'),
                         index_col='datetime',
                         date_parser=timeTMD,
                         parse_dates=True,dayfirst=True)

        dfT = dfT.dropna()
        dfT = dfT.truncate(before= datetimes.min() - pd.DateOffset(minutes=10),
                           after = datetimes.max() + pd.DateOffset(minutes=10))
        ts = pd.Series(index=datetimes).sort_index()
        col_label = dfT.ix[0,'location'].strip()
        df[col_label] = np.asarray(dfT['temp'].combine_first(ts).interpolate(method='values')[ts.index])
    return df

if __name__ == '__main__':

    data_file = r'I:\MSL\Private\LENGTH\CMM Leitz\ISO Verification\2013\small_test_unique_times.txt'
    folder = r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\Leitz Room\2013\2013-10'


    df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True, index_col=[3])
    df = df.iloc[:,:-1]
    dfT = retreive_temperatures_df_fixed(df, folder, ['Mobile.txt'])
    print('-------------------------')
    print(df.iloc[:,-1])
    print('-------------------------')
    data_file = r'I:\MSL\Private\LENGTH\Optical Projector\Light standards apertures\x_Air_unique_times_02b.txt'
    folder = r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\laser lab\2016\2016-4'


    df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True, index_col=[3])
    df = df.iloc[:,:-1]
    dfT = retreive_temperatures_df_fixed(df, folder, ['x_Air.txt'])
    print('-------------------------')
    print(df.iloc[:,-1])
    print('-------------------------')

