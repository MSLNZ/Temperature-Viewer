"""
program to display data from Temperature monitoring program
written using guiqwt
Uses the CurveWindow class to simplify layout and function.
"""
import time
t0 = time.time()
import sys


from guidata import qapplication
from guiqwt.plot import CurveWindow
from guiqwt.builder import make
from guidata.qt.QtGui import QWidget, QMenu
from guiqwt.styles import style_generator
from scales import DateTimeScaleEngine
from guiqwt.tools import DefaultToolbarID, CommandTool, OpenFileTool
from guiqwt.config import _
from guidata.qthelpers import get_std_icon, add_actions
from guidata.qt.compat import getopenfilenames
import os.path as osp
from guiqwt.interfaces import ICurveItemType
from guidata.qt.QtCore import QSize
from guidata.configtools import get_icon

from guidata.qt.QtCore import SIGNAL
from threading import Timer

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

class OpenFilesTool(OpenFileTool):
    """
    dialog box tool to open multiple files at once
    use ctrl or shift
    """
    def get_filenames(self, plot):
        """
        Opens a file dialog, returns list of filenames
        """
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        filenames, _f = getopenfilenames(plot, _("Open"),
                                       self.directory, self.formats)
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        filenames = [unicode(filename) for filename in filenames]
        if filenames:
            self.directory = osp.dirname(filenames[0])
        return filenames

    def activate_command(self, plot, checked):
        """Activate tool"""
        filenames = self.get_filenames(plot)
        if filenames:
            self.emit(SIGNAL("openfile(QString*)"), repr(filenames))

class RefreshTool(CommandTool):
    """
    button to activate rereading data files and adding to plot
    """
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        CommandTool.__init__(self, manager,title='Update',tip="Refresh Plot Data",
                             icon = get_std_icon("BrowserReload", 16),
                             toolbar_id=toolbar_id)
    def activate_command(self, plot, checked):
        """Activate tool"""
        print "Refresh Activated"
        self.emit( SIGNAL( 'refresh' ) )

class UpdateIntervalTool(CommandTool):
    """
    Adds a sub menu to the right click menu for setting the interval for
    automatically re-reading data from file
    """

    def __init__(self, manager):
        super(UpdateIntervalTool, self).__init__(manager, _("Update Interval"),
                                            tip=None, toolbar_id=None)
        self.action.setEnabled(True)

    def create_action_menu(self, manager):
        """Create and return menu for the tool's action"""
        menu = QMenu()
        int30 = manager.create_action("30 s",
                                        toggled=lambda state, interval=30:
                                        self.set_interval(state, interval))
        int60 = manager.create_action("60 s (1 min)",
                                        toggled=lambda state, interval=60:
                                        self.set_interval(state, interval))
        int300 = manager.create_action("300 s (5 mins)",
                                        toggled=lambda state, interval=300:
                                        self.set_interval(state, interval))
        int600 = manager.create_action("600 s (10 mins)",
                                        toggled=lambda state, interval=600:
                                        self.set_interval(state, interval))

        self.interval_menu = {int30: 30, int60: 60, int300: 300, int600: 600}

        add_actions(menu, (int30, int60, int300, int600))
        return menu

    def update_status(self, plot):
        for interval_action, interval_value in self.interval_menu.items():
            interval_action.setEnabled(True)
            if interval_value == self.manager.producer.interval:
                interval_action.setChecked(True)
            else:
                interval_action.setChecked(False)

    def set_interval(self, enable, interval):
        if enable:
            self.manager.producer.interval = interval

class Producer( QWidget ):
    '''Widget used to create a tokens producer and generate
    a PyQt signal every time.
    '''

    def __init__( self ):
        QWidget.__init__( self )
        self.interval = 30
        self.do = True
        self.start_timer()

    def produce( self ):
        '''This is the method who creates the new token and
        who emits the signal received by the MainWindow.
        '''
        self.start_timer()
        self.emit( SIGNAL( 'timedUpdate' ) )

    def start_timer( self ):
        '''Method used to create the new timer and to
        control the stop.
        '''
        if self.do:
            self.timer = Timer( self.interval, self.produce )
            self.timer.start()


class GuiQwtPlot( CurveWindow ):
    """
    class to do plot window
    """
    def __init__( self ):
        CurveWindow.__init__( self, toolbar=True,
                              options=dict(title="Temperature Data",
                                                xlabel='Time',
                                                ylabel=u'Temperature/deg C')  )
        self.setWindowTitle( 'Temperature Monitor Viewer' )
        self.resize(QSize(800, 300))


        self.producer = Producer()
        self.data = [ ]
        self.filenames = []
        self.line_style_gen = style_generator()

        self.connect( self.producer, SIGNAL( 'timedUpdate' ), self.update )

        self.plot = self.get_plot()
        self.plot.set_antialiasing( True )

        # Register extra toola (buttons on toolbar)
        opentool = self.add_tool( OpenFilesTool)
        opentool.directory = r'L:/Temperature Monitoring Data'
        opentool.formats = '*.txt'
        self.connect(opentool, SIGNAL("openfile(QString*)"), self.open_file)

        refreshtool = self.add_tool(RefreshTool)
        self.connect(refreshtool, SIGNAL( 'refresh' ), self.update)

        intervaltool = self.add_tool(UpdateIntervalTool)
        self.number_of_updates = 0

        # Create the Legend
        legend = make.legend( 'TL' )
        self.plot.add_item( legend )

        # Setup the plot's scale
        xaxis = self.plot.get_active_axes()[0]
        DateTimeScaleEngine.enableInAxis(self.plot, xaxis, rotation=-90)

    def __read_temperature_data(self, fname):
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

    def open_file(self, filenames):
        """
        opens files in filenames and adds data to plot
        """
        newfilenames = eval(str(filenames))
        #print newfilenames
        self.filenames.extend(newfilenames)
        if newfilenames:
            for filename in newfilenames:
                dates, values, label1, label2 = self.__read_temperature_data(filename)
                self.plot.add_item(make.curve(dates,
                                              values,
                                              title=label1+" "+label2,
                                              color=self.line_style_gen.next()[0]))
                self.plot.replot()

    def update(self):
        """
        rereads files and adds data to plot
        """
        if self.filenames:
            self.curves = self.plot.get_items(False, ICurveItemType)
            for i, filename in enumerate(self.filenames):
                dates, values, label1, label2 = self.__read_temperature_data(filename)
                self.curves[i].set_data(dates, values)
                print '.',
            self.plot.replot()
            print 'updated'
            #print 'interval', self.producer.interval

    def closeEvent( self, _ ):
        '''Method is run when the signal 'close' of the
        MainWindow is emited.
        '''
        self.producer.do = False

def main():
    """
    runs main program
    """
    app = qapplication()
    win = GuiQwtPlot( )
    win.show( )
    t1 = time.time()
    print 'time ',t1-t0
    app.exec_( )


if __name__ == '__main__':
    main()