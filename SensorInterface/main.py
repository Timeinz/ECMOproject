from BLE import BLE_module
from GUI_launcher import DesignerMainWindow
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication



if __name__ == "__main__":
    
    app = QApplication(sys.argv)


    gui = DesignerMainWindow()
    ble = BLE_module()

    ble.data_received.connect(gui.update_graph, type=Qt.ConnectionType.QueuedConnection)
    ble.notification_print.connect(gui.notification_printer)
    gui.send_message.connect(ble.send_message)
    gui.clear_graph.connect(ble.clear_graph)


    gui.show()
    sys.exit(app.exec())