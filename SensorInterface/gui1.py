# for command-line arguments
import sys
# Python Qt4 bindings for GUI objects
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
# Numpy functions for image creation
import numpy as np
# Matplotlib Figure object
from matplotlib.figure import Figure
# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
class Qt5MplCanvas(FigureCanvas):
    #Class to represent the FigureCanvas widget
    def __init__(self):
        # Standard Matplotlib code to generate the plot
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.x = np.arange(0.0, 3.0, 0.01)
        self.y = np.cos(2*np.pi*self.x)
        self.axes.plot(self.x, self.y)
        # initialize the canvas where the Figure renders into
        FigureCanvas.__init__(self, self.fig)
        #This material is copyright and is licensed for the sole use by Jillian Fraser on 20th November 2009
        #Download at WoweBook.Com
        #Embedding Matplotlib in Qt 4
        #[ 150 ]
# Create the GUI application
qApp = QApplication(sys.argv)
# Create the Matplotlib widget
mpl = Qt5MplCanvas()
# show the widget
mpl.show()
# start the Qt main loop execution, exiting from this script
# with the same return code of Qt application
sys.exit(qApp.exec_())