import time
import numpy as np
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import pyqtSignal
from gui import Ui_MplMainWindow


class DesignerMainWindow(QMainWindow, Ui_MplMainWindow):
    send_message = pyqtSignal(str)

    def __init__(self, parent = None, external = None):
        super(DesignerMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.start_button.clicked.connect(lambda: self.send_message.emit("mainstart"))
        self.stop_button.clicked.connect(lambda: self.send_message.emit("mainstop"))
        self.toggle_button.clicked.connect(lambda: self.send_message.emit("toggle"))
        
        #self.sensor.data_received.connect(self.update_graph, type=Qt.ConnectionType.QueuedConnection)

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
    
    def update_graph(self, data_list):
        #l, v = self.parse_file(self.mpllineEdit.text())
        self.mpl.canvas.ax.clear()
        self.mpl.canvas.ax.plot(data_list[0], data_list[1], label="ch0")
        self.mpl.canvas.ax.plot(data_list[0], data_list[2], label="ch1")
        self.mpl.canvas.ax.plot(data_list[0], data_list[3], label="ch2")
        self.mpl.canvas.ax.plot(data_list[0], data_list[4], label="ch3")
        self.mpl.canvas.ax.plot(data_list[0], data_list[5], label="ch4")
        self.mpl.canvas.ax.plot(data_list[0], data_list[6], label="ch5")
        self.mpl.canvas.ax.plot(data_list[0], data_list[7], label="ch6")
        self.mpl.canvas.ax.plot(data_list[0], data_list[8], label="ch7")
        self.mpl.canvas.ax.legend(loc="lower left")
        self.mpl.canvas.ax.grid(True)
        #self.mpl.canvas.ax.set_xlim(xmin=-0.25, xmax=len(l)-0.75)
        #self.mpl.canvas.ax.set_xticks(range(len(l)))
        #self.mpl.canvas.ax.set_xticklabels(l)
        #self.mpl.canvas.ax.get_yaxis().grid(True)
        self.mpl.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dmw = DesignerMainWindow()
    dmw.show()
    sys.exit(app.exec())

