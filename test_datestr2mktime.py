"""
Quick test of datestr2mktime from GuiQwtPlot_temperature.py
"""
import time

from GuiQwtPlot_temperature import datestr2mktime


def test_datestr2mktime():

    teststrs = [('14/01/2013 2:06:08 pm', [2013,1,14,14,6,8,0,0,-1]),
                ('7/11/2012 11:12:41 am', [2012,11,7,11,12,41,0,0,-1]),
                ('8/06/2012 11:08:05 a.m.',[2012,6,8,11,8,5,0,0,-1]),
                ('8/06/2012 11:08:05 am', [2012,6,8,11,8,5,0,0,-1]),
                ('8/06/2012 12:00:00 am', [2012,6,8,0,0,0,0,0,-1]),
                ('8/06/2012 12:00:00 pm', [2012,6,8,12,0,0,0,0,-1])]

    for teststr in teststrs:
        assert datestr2mktime(teststr[0]) == int(time.mktime(teststr[1]))

if __name__ == '__main__':
    test_datestr2mktime()