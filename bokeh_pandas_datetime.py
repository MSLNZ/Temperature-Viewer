# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:39:14 2017

@author: e.howick
"""

# minimal version of 
# https://anaconda.org/dhirschfeld/bokeh-timeseries-example/notebook
# as graph is zoomed time axis goes from mm/dd to 12h to :30
# how do we format differently? Using DatetimeTickFormatter?
# http://bokeh.pydata.org/en/latest/docs/reference/models/formatters.html
# can we get datetimes in correct format without using pandas
 

import numpy as np
from numpy.random import randn
from numpy import pi
import pandas as pd

import bokeh.plotting as plt
from bokeh.models.formatters import DatetimeTickFormatter


plt.output_file("datetime.html")

# Create a dummy timeseries
ndays = 100
dates = pd.date_range('01-Jan-2016', periods=48*ndays, freq='30T')
temp = np.cos(np.linspace(0, 2*pi*ndays, 48*ndays) + pi/2)
noise = np.cumsum(0.2*randn(temp.size))
temp = pd.Series(20 + 5*temp + noise, index=dates)


plot = plt.figure(
    width=800, height=600,
    x_axis_type="datetime",
    title="Temperature Forecast",
    title_text_font_size='14pt',
    tools="pan,wheel_zoom,box_zoom,reset",
    toolbar_location="above",
    x_axis_label='date'
)

plot.line(
    temp.index, temp.values,
    alpha=1, color='#E24A33', line_width=2,
    legend="temperature"
)

plot.xaxis.formatter=DatetimeTickFormatter(formats=dict(
        days=["%y-%m-%d"],
        months=["%y-%m"],
        hourmin = ["%y-%m-%d %H:%M"],
        hours=["%y-%m-%d %H:%M"],
        minutes=["%y-%m-%d %H:%M"]))
"""
microseconds = ['%fus'],
milliseconds = ['%3Nms', '%S.%3Ns'],
seconds = ['%Ss'],
minsec = [':%M:%S'],
minutes = [':%M', '%Mm'],
hourmin = ['%H:%M'],
hours = ['%Hh', '%H:%M'],
days = ['%m/%d', '%a%d'],
months = ['%m/%Y', '%b%y'],
years = ['%Y']),
"""

plt.show(plot)

