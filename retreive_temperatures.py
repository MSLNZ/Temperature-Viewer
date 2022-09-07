"""
24/6/14

given a pandas dataframe with an index of datetimes and a temperature file
finding function
produce a table of interpolated temperatures for the datetimes from the
temperature files.

TODO
produce veri
"""

import sys
import os
sys.path.append(r'L:\CMM Leitz\Ballplate_MSL\Python_analysis' )
sys.path.append(r'C:\Users\e.howick\Documents\_Projects\General')
import pandas as pd
import numpy as np

#file names before 2013-09-01
tmpfiles_01 = ['X1 Left.txt', 'Y2 Left.txt', 'Y1 Right.txt', 'Z1 Top.txt', 'Z1 Bottom.txt', 'Mobile.txt']

#file names after 2013-09-01
tmpfiles_02 = ['X1 Back.txt', 'Y2 Left.txt', 'Y1 Right.txt', 'Z1 Top.txt', 'Z1 Bottom.txt', 'Mobile.txt']

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
        print 'NA', temp
    return dt

def get_CMM_month_files(month):
    """
    month : string of form '2014-05'
    returns list of file names from CMM temperature monitoring folder
    for 2013 the month directories are 2013-05
    for 2014 the month directories are 2014-5
    """
    folder = r'L:\Temperature Monitoring Data\Leitz Room'
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

def process_datetimes_by_month(group, month_file_func):
    """
    this is called by the groupby transform function
    and returns a dataframe of temperatures
    """
    monthstr = group['monthstr'][0]
    file_list,dir_filed = month_file_func(monthstr)
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

        a1 = dfT['temp'].combine_first(ts)
        a2 = a1.interpolate(method='values')
        a3 = a2[ts.index]

        temp_series[col_label] = np.asarray(a3)

    return pd.DataFrame(temp_series, index=ts.index)

def retreive_temperatures_df(df, month_file_func):
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
    df['monthstr'] = df['year'].apply(str) + '-' + df['month'].apply(lambda x: str(x).zfill(2))
    df = df.drop('year',1)
    df = df.drop('month',1)
    #apply process_datetimes_by_month to each month using groupby
    df2 = df.groupby('monthstr').apply(process_datetimes_by_month, month_file_func=month_file_func)
    #put the two dataframes together
    df3 = pd.concat([df,df2],axis=1)
    return df3

def test_multi_months():
    #read in data file of all GB measurements, all measurements have unique times
    data_file = r'L:\CMM Leitz\ISO Verification\2013\all_data_parid_44_unique_times.txt'
    df = pd.read_csv(data_file, sep = '\t', header=0, parse_dates=[3], dayfirst=True,index_col=[3])
    df = df.iloc[:,:-1]
    df2 = retreive_temperatures_df(df, get_CMM_month_files)
    return df2

def test_single_month():
    dft = pd.DataFrame(np.random.randn(10,1),columns=['A'],index=pd.date_range('20130915',periods=10,freq='H'))
    df2 = retreive_temperatures_df(dft, get_CMM_month_files)
    return df2

def another_test():
    bp = pd.read_pickle(r'L:\CMM Leitz\Ballplate_MSL\ipy_notebooks\bp_01.pickle')
    df2 = retreive_temperatures_df(bp, get_CMM_month_files)
    return df2

def again():
    index = pd.to_datetime(('2013-09-18 09:41:48',
                        '2013-09-18 09:42:35',
                        '2013-09-18 09:43:30',
                        '2013-09-18 09:44:25',
                        '2013-09-18 09:45:19',
                        '2013-09-18 09:46:14',
                        '2013-09-18 09:47:09',
                        '2013-09-18 09:48:04',
                        '2013-09-18 09:48:58',
                        '2013-09-18 09:49:51',
                        '2013-09-18 09:50:45',
                        '2013-09-18 09:51:38',
                        '2013-09-18 09:52:31',
                        '2013-09-18 09:53:25',
                        '2013-09-18 09:54:18',
                        '2013-09-18 09:55:12',
                        '2013-09-18 09:56:07',
                        '2013-09-18 09:57:02',
                        '2013-09-18 09:57:57',
                        '2013-09-18 09:58:50'))
    df = pd.DataFrame(np.random.rand(20),index=index,columns=['rand'])
    df= df.ix[:1,:]
    df2 = retreive_temperatures_df(df, get_CMM_month_files)
    return df2

def without_groupby():
    df = pd.DataFrame(np.random.randn(10,1),columns=['A'],index=pd.date_range('20130928',periods=10,freq='H'))
    #add a column based on what month the measurements were made
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['monthstr'] = df['year'].apply(str) + '-' + df['month'].apply(lambda x: str(x).zfill(2))
    df = df.drop('year',1)
    df = df.drop('month',1)
    df2 = process_datetimes_by_month(df, get_CMM_month_files)
    print df2


if __name__ == '__main__':
##   df = test_multi_months()
##   print df.head()
##   print df.tail()
##   print df.count()

##   df = test_single_month()
##   print df

   df = another_test()
   print df


