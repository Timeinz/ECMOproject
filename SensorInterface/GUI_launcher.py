import time
import numpy as np
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import pyqtSignal
from PyQt6 import QtGui
from gui import Ui_MplMainWindow

from datetime import datetime


class DesignerMainWindow(QMainWindow, Ui_MplMainWindow):
    send_message = pyqtSignal(str)

    def __init__(self, parent = None, external = None):
        super(DesignerMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.start_button.clicked.connect(lambda: self.send_message.emit("mainstart"))
        self.stop_button.clicked.connect(lambda: self.send_message.emit("mainstop"))
        self.toggle_button.clicked.connect(lambda: self.send_message.emit("toggle"))

        self.x_time = []
        self.trim = 0
        
        #self.sensor.data_received.connect(self.update_graph, type=Qt.ConnectionType.QueuedConnection)
    
    def update_graph(self, data_list):
        #l, v = self.parse_file(self.mpllineEdit.text())
        self.mpl.canvas.ax.clear()
        self.x_time.append(datetime.strptime(str(data_list[0][-1]), '%Y%m%d%H%M%S%f'))
        self.trim = len(self.x_time) - len(data_list[0])
        del self.x_time[:self.trim]
        self.mpl.canvas.ax.plot(self.x_time, data_list[1], label="ch0")
        self.mpl.canvas.ax.plot(self.x_time, data_list[2], label="ch1")
        self.mpl.canvas.ax.plot(self.x_time, data_list[3], label="ch2")
        self.mpl.canvas.ax.plot(self.x_time, data_list[4], label="ch3")
        self.mpl.canvas.ax.plot(self.x_time, data_list[5], label="ch4")
        self.mpl.canvas.ax.plot(self.x_time, data_list[6], label="ch5")
        self.mpl.canvas.ax.plot(self.x_time, data_list[7], label="ch6")
        self.mpl.canvas.ax.plot(self.x_time, data_list[8], label="ch7")
        self.mpl.canvas.ax.legend(loc="lower left")
        self.mpl.canvas.ax.grid(True)
        #self.mpl.canvas.ax.set_xlim(xmin=-0.25, xmax=len(l)-0.75)
        #self.mpl.canvas.ax.set_xticks(range(len(l)))
        #self.mpl.canvas.ax.set_xticklabels(l)
        #self.mpl.canvas.ax.get_yaxis().grid(True)
        self.mpl.canvas.draw()
        self.box_data.append(str(list(data_list[i][-1] for i in range (9))))
    
    def notification_printer(self, message, remote):
        if remote:
            self.box_notification.append(f'<span style="color: red;">PICO: {message}</span>')
        else:
            self.box_notification.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dmw = DesignerMainWindow()
    dmw.show()
    sys.exit(app.exec())

