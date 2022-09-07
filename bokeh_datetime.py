import time
import pandas as pd
from bokeh.plotting import figure, output_file, show

def datestr2mktime(dtstr):
    """
    convert 8/06/2012 11:08:05 a.m. to seconds since the epoch
    also convert 8/06/2012 11:08:05 am
    this code takes 0.35 s on a 22481 line file
    and is faster than using time module functions
    """
    date, tim, apm = dtstr.split()
    day, month, year = date.split('/')
    h, m, s = tim.split(':')
    if apm[0] == 'a' and int(h) == 12:
        h = 0
    if apm[0] == 'p' and int(h) !=12:
        h = int(h) + 12
    #the -1 for the daylight saving flag means the results are plotted as recorded in file
    tt = [year, month, day, h, m, s, 0, 0, -1]
    tt = tuple([int(v) for v  in tt])
    ts = int(time.mktime(tt))
    return ts
    
def read_temperature_data(fname):
    """
    reads data in from file of form

    Automatically Generated File!

    19.9475379495647, 1,7/11/2012 11:12:41 am, LEITZ, X1 Left
    19.9447869860416, 1,7/11/2012 11:14:30 am, LEITZ, X1 Left
    19.9497490060749, 1,7/11/2012 11:16:00 am, LEITZ, X1 Left
    19.9436814593114, 1,7/11/2012 11:17:19 am, LEITZ, X1 Left

    """
    #1.8 s for 22481 line file and is faster than using csv module functions
    #t0 = time.time()
    f = open(fname, "r")
    s0 = f.read()
    f.close()
    s1 = s0.splitlines()
    s2 = [s.split(',') for s in s1 if s != '']
    #t1 = time.time()
    data = [[float(s[0]), datestr2mktime(s[2])] for s in s2[2:]]
    #print "time conversion", time.time() - t1
    values, dates = zip(*data)
    label1 = s2[2][3]
    label2 = s2[2][4]
    #print "total read time", time.time() - t0
    return dates, values, label1, label2



output_file("datetime.html")

# create a new plot with a datetime axis type
p = figure(width=800, height=250, x_axis_type="datetime")
filename = r'L:\Temperature Monitoring Data\laser lab\2017\2017-1\x_Air.txt'
dates, values, label1, label2 = read_temperature_data(filename)
p.line(dates, values, color='navy', alpha=0.5)

show(p)
