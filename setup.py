import sys
import os

"""Create a stand-alone executable"""

try:
    import guidata
    from guidata.disthelpers import Distribution
except ImportError:
    raise ImportError, "This script requires guidata 1.4+"



def create_executable():
    """Build executable using ``guidata.disthelpers``"""
    dist = Distribution()
    dist.setup(name='Foo', version='0.1',
           description='bar',
           script="GuiQwtPlot_temperature.py", target_name='GuiQwtPlot_temperature.exe')
    dist.add_modules('guidata', 'guiqwt')
    # Building executable
    dist.build('cx_Freeze')

if __name__ == '__main__':
    create_executable()