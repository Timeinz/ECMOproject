import time
import numpy as np
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import Qt, QThread
from qtdesigner import Ui_MplMainWindow

#from blablabl import sensor_signal

class DesignerMainWindow(QMainWindow, Ui_MplMainWindow):
    def __init__(self, parent = None, external = None):
        super(DesignerMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.mplpushButton.clicked.connect(self.update_graph)
        self.mplactionOpen.triggered.connect(self.select_file)
        self.mplactionQuit.triggered.connect(QApplication.quit)
        
        #Connect external signal to update function
        self.sensor = external
        self.sensor_thread = QThread()
        self.sensor.moveToThread(self.sensor_thread)
        self.sensor_thread.start()
        print("moved the thread")
        self.sensor.data_received.connect(self.update_graph, type=Qt.ConnectionType.QueuedConnection)

    def select_file(self):
        file = QFileDialog.getOpenFileName()
        if file:
            self.mpllineEdit.setText(file[0])

    def parse_file(self, filename):
        letters = {}
        for i in range(97, 122 + 1):
            letters[chr(i)] = 0
        
        with open(filename) as f:
            for line in f:
                for char in line:
                    # counts only letters
                    if ord(char.lower()) in range(97, 122 + 1):
                        letters[char.lower()] += 1
        
        k = sorted(letters.keys())
        v = [letters[ki] for ki in k]
        return k, v
    
    def update_graph(self):
        l, v = self.parse_file(self.mpllineEdit.text())
        self.mpl.canvas.ax.clear()
        self.mpl.canvas.ax.bar(np.arange(len(l))-0.25, v, width=0.5)
        self.mpl.canvas.ax.set_xlim(xmin=-0.25, xmax=len(l)-0.75)
        self.mpl.canvas.ax.set_xticks(range(len(l)))
        self.mpl.canvas.ax.set_xticklabels(l)
        self.mpl.canvas.ax.get_yaxis().grid(True)
        self.mpl.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dmw = DesignerMainWindow()
    dmw.show()
    sys.exit(app.exec())

