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

def retreive_temperatures_df(df, folder, file_list, date_col=None):
    """
    df          is a dataframe with an index of datetimes
    folder      is a string pointing to a directory of files written by the
                temperature monitoring program
    file_list   list of filenames to examine for temperatures

    date_col    column to use for datetimes if date_col=None uses index

    returns df with an extra column of temperatures added for each file in file_list

    """

    if type(date_col) == int:
        datetimes = df.iloc[:,date_col].copy()
    else:
        datetimes = df.index
    #print datetimes.head()


    if datetimes.min().month != datetimes.max().month:
        print("warning data spans multiple months")
    yearstr = str(datetimes.min().year)
    monthstr = yearstr + '-' + str(datetimes.min().month)
    dir_filed = os.path.join(folder, yearstr, monthstr)
    if not(os.path.isdir(dir_filed)):
        monthstr = yearstr + '-' + str(datetimes.min().month).zfill(2)
        dir_filed = os.path.join(folder, yearstr, monthstr)
    print (dir_filed)
    #interpolate temperatures
    for fn in file_list:
        fname = os.path.join(dir_filed,fn)
        dfT = pd.read_csv(fname,sep=',',skiprows=2,
                         names=('temp','channel','datetime','room','location'),
                         index_col='datetime',
                         date_parser=timeTMD,
                         parse_dates=True,dayfirst=True)
        #print type(dfT.index)
        dfT = dfT.dropna()
        dfT = dfT.truncate(before= datetimes.min() - pd.DateOffset(minutes=10),
                           after = datetimes.max() + pd.DateOffset(minutes=10))
        ts = pd.Series(index=datetimes).sort_index()
        col_label = dfT.ix[0,'location'].strip()
        df[col_label] = np.asarray(dfT['temp'].combine_first(ts).interpolate(method='values')[ts.index])


    return df

def get_month_files(month):
    """
    month : string of form '2014-05'
    returns list of file names from CMM tempaertaure monitoring
    """
    folder = r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\laser lab'
    yearstr = month[:4]
    dir_filed = os.path.join(folder, yearstr, month)
    if not(os.path.isdir(dir_filed)):
        #remove leading zero on month
        month = yearstr + '-' + month[-1]
        dir_filed = os.path.join(folder, yearstr, month)
    #print dir_filed
    #get correct file list
    if month < '2013-09':
        file_list = tmpfiles_01
    else:
        file_list = tmpfiles_02
    return file_list, dir_filed

def retreive_temperatures_CMM_df(df, folder, date_col=None):
    """
    df          is a dataframe with an index of datetimes
    folder      is a string pointing to a directory of files written by the
                temperature monitoring program
    date_col    column to use for datetimes if date_col=None uses index

    returns df with an extra column of temperatures added for each file in file_list
    works for datetimes spanning multiple months
    """

    if type(date_col) == int:
        datetimes = df.iloc[:,date_col].copy()
    else:
        datetimes = df.index
    print (datetimes.head())

    s = datetimes.apply(lambda row: str(row.year) + '-' + str(row.month).zfill(2))
    dt = pd.DataFrame({'datetime':datetimes, 'monthstr': s})
    months = dt['monthstr'].unique()

    for month in months:
        #load files for that month
        yearstr = month[:4]
        dir_filed = os.path.join(folder, yearstr, monthstr)
        if not(os.path.isdir(dir_filed)):
            #remove leading zero on month
            monthstr = yearstr + '-' + month[-1]
            dir_filed = os.path.join(folder, yearstr, monthstr)
        print (dir_filed)
        #get correct file list
        if month < '2013-09':
            file_list = tmpfiles_01
        else:
            file_list = tmpfiles_02
        #get data for month
        dt_month = dt[dt['monthstr'] == month]
    #interpolate temperatures
    for fn in file_list:
        fname = os.path.join(dir_filed,fn)
        dfT = pd.read_csv(fname,sep=',',skiprows=2,
                         names=('temp','channel','datetime','room','location'),
                         index_col='datetime',
                         date_parser=timeTMD,
                         parse_dates=True,dayfirst=True)

        dfT = dfT.truncate(before= datetimes.min() - pd.DateOffset(minutes=10),
                           after = datetimes.max() + pd.DateOffset(minutes=10))
        ts = pd.Series(index=datetimes).sort_index()
        col_label = dfT.ix[0,'location'].strip()
        df[col_label] = np.asarray(dfT['temp'].combine_first(ts).interpolate(method='values')[ts.index])


    return df

def test_retreive_temperatures(dc):
    #read in a gauge block measurement file
    data = """2014-05-05 14:40:53

    769.56969,41.74589, -296.40539
    -0.69227,0.59328, 0.41083
    -0.50781,-0.80499, 0.30679
    0.51273,0.00375, 0.85854

    No TC
    2014-05-05 14:05:43, 99.99896
    2014-05-05 14:06:24, 124.9985
    2014-05-05 14:07:13, 149.99844
    2014-05-05 14:08:04, 174.99842
    2014-05-05 14:08:56, 199.99831
    2014-05-05 14:09:51, 249.99848
    2014-05-05 14:10:47, 299.99853
    2014-05-05 14:11:48, 399.99832
    2014-05-05 14:12:53, 499.99869
    2014-05-05 14:14:05, 599.99873"""

    if dc:
        df = pd.read_csv(StringIO(data), sep=',', skiprows=8,
                                         names=('datetime','length'),
                                         parse_dates=[0])
        df = retreive_temperatures_df(df,
                                  r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\laser lab',
                                  tmpfiles_02[0:1] ,date_col=0)
    else:
        df = pd.read_csv(StringIO(data), sep=',', skiprows=8,
                                         names=('datetime','length'),
                                         index_col='datetime', parse_dates=True)

        df = retreive_temperatures_df(df,
                                      r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\laser lab',
                                      tmpfiles_02[0:1])
    print (df)

def test_2013_file():
    fname = r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\laser lab\2016\2016-3\X_Air.txt'
    dfT = pd.read_csv(fname,sep=',',skiprows=2,
                         names=('temp','channel','datetime','room','location'),
                         index_col='datetime',
                         date_parser=timeTMD,
                         parse_dates=True,dayfirst=True)
    print (type(dfT.index))
    print (dfT.head())

#def test_gbs():
    #data_file = r'L:\CMM Leitz\ISO Verification\2013\all_data_parid_44.txt'
    #df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True)
    #df = retreive_temperatures_df(df,
                              #r'L:\Temperature Monitoring Data\Leitz Room',
                              #tmpfiles_02,date_col=3)
def test_single_month(month):
    #read in data file of all measurements, all measurements have unique times
    data_file = r'I:\MSL\Private\LENGTH\Optical Projector\Light standards apertures\x_Air_unique_times.txt'
    df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True,index_col=[3])
    df = df.iloc[:,:-1]
    #add a column based on what month the measurements were made
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['monthstr'] = '2016-3'
    df = df.drop('year',1)
    df = df.drop('month',1)
    #select the corect month
    dfmonth = df[df['monthstr'] == month]
    file_list,dir_filed = get_month_files(month)
    dfT = retreive_temperatures_df(dfmonth, r'I:\MSL\Private\LENGTH\Temperature Monitoring Data\laser lab', file_list)
    return dfT

def process_datetimes_by_month(group, month_file_func):
    """
    this is called by the groupby transform function
    and returns a dataframe of temperatures
    """
    monthstr = group['monthstr'][0]
    file_list,dir_filed = month_file_func(monthstr)
    #print file_list
    ts = pd.Series(index = group.index)
    temp_series = {}
    for fn in file_list:
        fname = os.path.join(dir_filed,fn)
        dfT = pd.read_csv(fname,sep=',',skiprows=2,
                         names=('temp','channel','datetime','room','location'),
                         index_col='datetime',
                         date_parser=timeTMD,
                         parse_dates=True,dayfirst=True)
        dfT = dfT.dropna()
        dfT = dfT.truncate(before= ts.index.min() - pd.DateOffset(minutes=10),
                           after = ts.index.max() + pd.DateOffset(minutes=10))
        col_label = dfT.ix[0,'location'].strip()
        temp_series[col_label] = np.asarray(dfT['temp'].combine_first(ts).interpolate(method='values')[ts.index])

    return pd.DataFrame(temp_series, index=ts.index)


def test_dfT(fname):
    dfT = pd.read_csv(fname,sep=',',skiprows=2,
                         names=('temp','channel','datetime','room','location'),
                         index_col='datetime',
                         date_parser=timeTMD,
                         parse_dates=True,dayfirst=True)
    return dfT


#def test_groupby():
#    #read in data file of all measurements, all measurements have unique times
#    data_file = r'L:\CMM Leitz\ISO Verification\2013\all_data_parid_44_unique_times.txt'
#    df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True,index_col=[3])
#    df = df.iloc[:,:-1]
#    #add a column based on what month the measurements were made
#    df['year'] = df.index.year
#    df['month'] = df.index.month
#    df['monthstr'] = df['year'].apply(str) + '-' + df['month'].apply(lambda x: str(x).zfill(2))
#    df = df.drop('year',1)
#    df = df.drop('month',1)
#    #apply process_datetimes_by_month to each month using groupby
#    df2 = df.groupby('monthstr').apply(process_datetimes_by_month, month_file_func=get_month_files)
#    #put the two dataframes together
#    df3 = pd.concat([df,df2],axis=1)
#    return df3

def retreive_temperatures_df_multi_months(df, month_file_func):
    """
    df                 is a dataframe with an index of datetimes

    month_file_func    is a function that takes a string like '2014-05' and
                       returns file_list   list of file names eg.  ['X1 Front.txt', 'Mobile.txt']
                               dir_filed    string containing folder path of files
                       for that month, see get_month_files for an example for the CMM

    returns df with an extra column of temperatures added for each file in file_list
    works for datetimes spanning multiple months
    """
    #add a column based on what month the measurements were made
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['monthstr'] = '2016-3'
    df = df.drop('year',1)
    df = df.drop('month',1)
    #apply process_datetimes_by_month to each month using groupby
    df2 = df.groupby('monthstr').apply(process_datetimes_by_month, month_file_func=month_file_func)
    #put the two dataframes together
    df3 = pd.concat([df,df2],axis=1)
    return df3

def test_multi_months():
    #read in data file of all GB measurements, all measurements have unique times
    data_file = r'I:\MSL\Private\LENGTH\Optical Projector\Light standards apertures\x_Air_unique_times.txt'
    df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True,index_col=[3])
    df = df.iloc[:,:-1]
    df2 = retreive_temperatures_df_multi_months(df, get_month_files)
    return df2



if __name__ == '__main__':

   dfT = test_single_month('2016-03')

   dfT.to_csv(r'C:')

