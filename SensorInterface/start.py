try:
    import sys
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
                                QHBoxLayout, QLineEdit, QLabel, QSpacerItem, QSizePolicy)
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtGui import QDoubleValidator, QColor, QPalette, QFont
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import random
    import time
    from datetime import datetime, timedelta
    import matplotlib.dates as mdates
    import numpy as np
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    sys.exit(1) 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-time Data Stream")
        self.setGeometry(100, 100, 800, 500)

        # Dark Mode Styling with metallic blue background
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1E2E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4A4A5A;
                border: none;
                border-radius: 15px;
                color: #FFFFFF;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5A5A6A;
            }
            QPushButton:checked, QPushButton:pressed {
                background-color: #6B5A8A;
            }
            QLineEdit {
                background-color: #2A2E3E;
                border: 1px solid #3A3E4E;
                border-radius: 5px;
                color: #FFFFFF;
            }
            QLabel {
                color: #BDBDBD;
            }
        """)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create Figure and Canvas
        self.figure = Figure(figsize=(6, 4), dpi=150, facecolor='#1A1E2E')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1E2235')
        self.canvas = FigureCanvas(self.figure)
        
        # Enable high-quality text rendering
        self.figure.set_tight_layout(True)
        for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label]:
            text.set_path_effects([])  # Reset any existing effects
            text.set_rasterized(True)  # Enable text rasterization
        
        # Enable high-quality rendering for tick labels
        for tick in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            tick.set_path_effects([])
            tick.set_rasterized(True)
        
        # Initialize plot parameters
        self.window_duration = 60  # Show 60 seconds of data
        self.ax.set_title('Real-time Data Stream', color='#FFFFFF', pad=20)
        self.ax.set_xlabel('Time', color='#FFFFFF', labelpad=10)
        self.ax.set_ylabel('Value', color='#FFFFFF', labelpad=10)
        self.ax.tick_params(axis='x', colors='#FFFFFF', rotation=45)
        self.ax.tick_params(axis='y', colors='#FFFFFF')
        self.ax.grid(True, color='#2A2E4E', antialiased=False)  # Crisp grid
        
        # Configure date formatting
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        for spine in self.ax.spines.values():
            spine.set_color('#3A3E4E')  # Metallic border color

        # Data storage
        self.timestamps = []
        self.values = []
        # Set crisp, non-antialiased lines for the plot
        self.line, = self.ax.plot([], [], color='#8A9FD1', linewidth=2, 
                                 antialiased=False, linestyle='-',
                                 snap=True)  # Snap to pixel grid

        # Add vertical spacer for padding
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Controls layout
        controls_layout = QVBoxLayout()

        # Start/Stop button
        self.start_stop_button = QPushButton('Start/Stop')
        self.start_stop_button.setFont(QFont("Arial", 10))
        self.start_stop_button.setCheckable(True)
        self.start_stop_button.clicked.connect(self.toggle_stream)
        controls_layout.addWidget(self.start_stop_button)

        # Autoscale button
        self.autoscale_button = QPushButton('Autoscale Y')
        self.autoscale_button.setFont(QFont("Arial", 10))
        self.autoscale_button.setCheckable(True)
        self.autoscale_button.clicked.connect(self.autoscale_y)
        controls_layout.addWidget(self.autoscale_button)

        # Y-axis range controls
        y_range_layout = QHBoxLayout()
        y_range_layout.addWidget(QLabel("Lower Y:"))
        self.lower_y_input = QLineEdit("0")
        self.lower_y_input.setValidator(QDoubleValidator())
        y_range_layout.addWidget(self.lower_y_input)
        y_range_layout.addWidget(QLabel("Upper Y:"))
        self.upper_y_input = QLineEdit("100")
        self.upper_y_input.setValidator(QDoubleValidator())
        y_range_layout.addWidget(self.upper_y_input)
        self.set_y_range_button = QPushButton('Set Y Range')
        self.set_y_range_button.setCheckable(True)
        self.set_y_range_button.clicked.connect(self.set_y_range)
        y_range_layout.addWidget(self.set_y_range_button)
        controls_layout.addLayout(y_range_layout)

        layout.addLayout(controls_layout)

        # Timer setup
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.generate_data)
        
        self.stream_active = False
        self.autoscale = True
        self.last_manual_lower = 0
        self.last_manual_upper = 100

    def toggle_stream(self):
        if not self.stream_active:
            self.timestamps = []
            self.values = []
            self.update_timer.start(100)  # Update plot every 200ms
            self.generate_data()  # Generate first data point
            self.data_timer.start(random.randint(100, 1000))  # Random data generation interval
            self.start_stop_button.setChecked(True)
        else:
            self.update_timer.stop()
            self.data_timer.stop()
            self.start_stop_button.setChecked(False)
        self.stream_active = not self.stream_active

    def generate_data(self):
        if self.stream_active:
            current_time = datetime.now()
            new_value = random.randint(0, 100)
            self.timestamps.append(mdates.date2num(current_time))
            self.values.append(new_value)
            
            # Set next random interval for data generation
            self.data_timer.setInterval(random.randint(100, 1000))

    def update_plot(self):
        if not self.timestamps:
            return

        current_time = mdates.date2num(datetime.now())
        
        # Remove old data points
        cutoff_time = current_time - (self.window_duration / (24 * 3600))  # Convert seconds to days
        while self.timestamps and self.timestamps[0] < cutoff_time:
            self.timestamps.pop(0)
            self.values.pop(0)

        # Update plot data with interpolation
        if len(self.timestamps) > 1:
            # Create smoother interpolated data
            interp_times = np.linspace(min(self.timestamps), max(self.timestamps), len(self.timestamps) * 3)
            interp_values = np.interp(interp_times, self.timestamps, self.values)
            self.line.set_data(interp_times, interp_values)
        else:
            self.line.set_data(self.timestamps, self.values)
        
        # Update x-axis limits to show sliding window
        self.ax.set_xlim(current_time - (self.window_duration / (24 * 3600)), current_time)
        
        # Update y-axis based on autoscale setting
        if self.autoscale and self.values:
            y_min, y_max = min(self.values), max(self.values)
            padding = (y_max - y_min) * 0.10 if y_max != y_min else 10
            self.ax.set_ylim(y_min - padding, y_max + padding)
        
        # Use smooth rendering
        self.canvas.draw()

    def autoscale_y(self):
        self.autoscale = not self.autoscale
        self.autoscale_button.setChecked(self.autoscale)
        self.lower_y_input.setEnabled(not self.autoscale)
        self.upper_y_input.setEnabled(not self.autoscale)
        if self.autoscale:
            self.set_y_range_button.setChecked(False)

    def set_y_range(self):
        self.autoscale = False
        self.autoscale_button.setChecked(False)
        self.set_y_range_button.setChecked(True)
        
        try:
            lower = float(self.lower_y_input.text())
            upper = float(self.upper_y_input.text())
            if lower >= upper:
                raise ValueError("Lower limit must be less than upper limit.")
            self.last_manual_lower = lower
            self.last_manual_upper = upper
            self.ax.set_ylim(lower, upper)
        except ValueError:
            self.lower_y_input.setText(str(self.last_manual_lower))
            self.upper_y_input.setText(str(self.last_manual_upper))
            self.ax.set_ylim(self.last_manual_lower, self.last_manual_upper)

        self.lower_y_input.setEnabled(True)
        self.upper_y_input.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())