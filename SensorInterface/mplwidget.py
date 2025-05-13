from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout
from matplotlib.backends.backend_qtagg \
            import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                    QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)

class MplWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)