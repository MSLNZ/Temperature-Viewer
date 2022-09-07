# -*- coding: utf-8 -*-
#
# Copyright © 2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see guidata/__init__.py for details)

"""
guidata.disthelpers demo

How to create an executable with py2exe or cx_Freeze with less efforts than
writing a complete setup script.
"""


from guidata.disthelpers import Distribution

if __name__ == '__main__':
    dist = Distribution()
    dist.setup(name="Temperature Viewer", version='1.0.0',
               description="View Temperature Data",
               script="GuiQwtPlot_temperature.py", target_name="temperature_view.exe")
    dist.add_modules('guidata', 'guiqwt')
    dist.build('cx_Freeze')

