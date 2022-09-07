import guidata
from guiqwt.plot import ImageDialog
from guiqwt.builder import make

_app = guidata.qapplication()

class VerySimpleDialog(ImageDialog):
    def set_data(self, data):
        plot = self.get_plot()
        item = make.trimage(data)
        plot.add_item(item, z=0)
        plot.set_active_item(item)
        plot.replot()

if __name__ == "__main__":
    import numpy as np
    from guidata import qapplication
    qapplication()
    dlg = VerySimpleDialog()
    dlg.set_data(np.random.rand(100, 100))
    dlg.exec_()
