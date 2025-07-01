import csv
import os
import random
import struct

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QSizePolicy, QGroupBox, QSpacerItem, QLineEdit, QFileDialog,QMessageBox
)
from PyQt5.QtCore import QThread, Qt, QEvent, QTimer
import pyqtgraph as pg

from graph_plotting_functionalities.plotting import Signal_list
from src.data_logger import DataLogger
from src.data_worker import DataWorker
from graph_plotting_functionalities.Graph_Template import GraphTemplate


def create_button_row(pairs):
    row = QHBoxLayout()
    for label, slot in pairs:
        btn = QPushButton(label)
        btn.setFixedSize(100, 30)
        btn.clicked.connect(slot)
        row.addWidget(btn)
    return row


class GraphWidget(QWidget):
    def __init__(self, graph_id, mode="operation", signal1="Sin", signal2="Cos", num=1):
        super().__init__()
        self.graph_id = graph_id
        self.mode = mode
        self.signal_name = signal1
        self.signal_func = Signal_list[signal1]
        self.dt = 0.05

        self.pen_color = self.generate_color()
        self.pen_width = 3
        self.curve = None
        self.logger = None
        self.is_logging = False

        self.initUI()
        self.setup_worker()
        self.destination.installEventFilter(self)
        self.logging_timer = QTimer()
        self.logging_timer.setInterval(500)
        self.logging_timer.timeout.connect(self.log_periodically)

    def log_periodically(self):
        if self.is_logging and self.logger:
            #if both start log pressed and logger is active
            if  self.logger_combo_box.currentText()=="CSV":
                self.logger.logg_csv()
            elif self.logger_combo_box.currentText()=="Binary":
                self.logger.logg_binary()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # === Graph Section ===
        self.create_graph_section(main_layout)

        # === Control Panel ===
        self.create_control_panel(main_layout)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_graph_section(self, parent_layout):
        """Create the graph plotting area"""
        self.graph_template = GraphTemplate(
            title=f"Graph {self.graph_id}",
            xlabel="Time (s)",
            ylabel="Amplitude",
            legend=True,
        )
        self.graph_template.plot.enableAutoRange(False)
        pen = pg.mkPen(color=self.pen_color, width=self.pen_width)
        self.curve = self.graph_template.plot.plot([], [], pen=pen, name=self.signal_name)
        parent_layout.addWidget(self.graph_template)

    def create_control_panel(self, parent_layout):
        """Create the main control panel with organized sections"""
        controls_box = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        controls_layout.setContentsMargins(15, 15, 15, 15)

        # Add control sections
        self.create_playback_controls(controls_layout)
        self.add_vertical_separator(controls_layout)
        self.create_zoom_controls(controls_layout)
        self.add_vertical_separator(controls_layout)
        self.create_logging_controls(controls_layout)

        controls_box.setLayout(controls_layout)
        parent_layout.addWidget(controls_box)

    def create_playback_controls(self, parent_layout):
        """Create playback control buttons section"""
        playback_group = QGroupBox("Playback")
        playback_layout = QVBoxLayout()
        playback_layout.setSpacing(8)

        # Create buttons
        self.start_btn = QPushButton('Start')
        self.stop_btn = QPushButton('Stop')
        self.reset_btn = QPushButton('Reset')

        buttons = [self.start_btn, self.stop_btn, self.reset_btn]
        for btn in buttons:
            btn.setFixedSize(100, 30)
            playback_layout.addWidget(btn)

        # Set tooltips
        self.start_btn.setToolTip("Start signal plotting")
        self.stop_btn.setToolTip("Stop signal plotting")
        self.reset_btn.setToolTip("Clear and restart the plot")

        # Connect signals
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.reset_btn.clicked.connect(self.on_reset_clicked)

        playback_group.setLayout(playback_layout)
        parent_layout.addWidget(playback_group)

    def create_zoom_controls(self, parent_layout):
        """Create zoom control section"""
        zoom_group = QGroupBox("Zoom & Scale")
        zoom_layout = QVBoxLayout()
        zoom_layout.setSpacing(8)

        # Zoom axis selection
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("Axis:"))
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setFixedWidth(80)
        self.zoom_combo_box.setToolTip("Choose axis to zoom")
        axis_layout.addWidget(self.zoom_combo_box)
        axis_layout.addStretch()
        zoom_layout.addLayout(axis_layout)

        # Zoom buttons
        self.zoom_in_btn = QPushButton('＋ Zoom In')
        self.zoom_out_btn = QPushButton('－ Zoom Out')
        self.auto_scale_btn = QPushButton('Auto Scale')

        zoom_buttons = [self.zoom_in_btn, self.zoom_out_btn, self.auto_scale_btn]
        for btn in zoom_buttons:
            btn.setFixedSize(100, 30)
            zoom_layout.addWidget(btn)

        # Set tooltips
        self.zoom_in_btn.setToolTip("Zoom in the selected axis")
        self.zoom_out_btn.setToolTip("Zoom out the selected axis")
        self.auto_scale_btn.setToolTip("Automatically scale plot to fit data")

        # Connect signals
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.auto_scale_btn.clicked.connect(self.auto_scale)

        zoom_group.setLayout(zoom_layout)
        parent_layout.addWidget(zoom_group)

    def create_logging_controls(self, parent_layout):
        """Create data logging control section"""
        logging_group = QGroupBox("Data Logging")
        logging_layout = QVBoxLayout()
        logging_layout.setSpacing(10)

        # File format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.logger_combo_box = QComboBox()
        self.logger_combo_box.addItems(["Select format", "CSV", "Binary"])
        self.logger_combo_box.setFixedWidth(100)
        self.logger_combo_box.setToolTip("Select file format for data logging")
        format_layout.addWidget(self.logger_combo_box)
        format_layout.addStretch()
        logging_layout.addLayout(format_layout)

        # Max file size selection
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1MB", "5MB", "10MB", "50MB", "100MB"])
        self.size_combo.setFixedWidth(100)
        self.size_combo.setToolTip("Max size for each log file")
        size_layout.addWidget(self.size_combo)
        size_layout.addStretch()
        logging_layout.addLayout(size_layout)

        # Destination folder
        folder_layout = QVBoxLayout()
        folder_layout.addWidget(QLabel("Destination:"))
        self.destination = QLineEdit()
        self.destination.setReadOnly(True)
        self.destination.setFixedWidth(200)
        self.destination.setPlaceholderText("Click to select folder...")
        self.destination.setCursor(Qt.PointingHandCursor)
        folder_layout.addWidget(self.destination)
        logging_layout.addLayout(folder_layout)

        # Logging action buttons
        button_layout = QHBoxLayout()
        self.start_log_btn = QPushButton("Start Log")
        self.stop_log_btn = QPushButton("Stop Log")
        self.stop_log_btn.setEnabled(False)

        for btn in [self.start_log_btn, self.stop_log_btn]:
            btn.setFixedSize(90, 30)
            button_layout.addWidget(btn)

        self.start_log_btn.clicked.connect(self.on_start_logging)
        self.stop_log_btn.clicked.connect(self.on_stop_logging)

        logging_layout.addLayout(button_layout)
        logging_group.setLayout(logging_layout)
        parent_layout.addWidget(logging_group)

    def add_vertical_separator(self, layout):
        """Add a vertical separator line between sections"""
        separator = QSpacerItem(1, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout.addItem(separator)

    def generate_color(self):
        chars = '0123456789ABCDEF'
        return "#" + "".join(random.choice(chars) for _ in range(6))

    def setup_worker(self):
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt, signal_func=self.signal_func)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

    def clean_up_worker(self):
        if self.worker:
            self.worker.stop_work()
            try:
                self.worker.data_ready.disconnect()
            except TypeError:
                pass
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

    def update_plot(self, t, y1, y2=None):
        self.curve.setData(t, y1)

    def on_start_clicked(self):
        if not self.worker_thread.isRunning():
            self.worker_thread.started.connect(self.worker.start_work)
            self.worker_thread.start()

    def on_stop_clicked(self):
        if hasattr(self, "worker") and self.worker:
            self.worker.stop_work()
        if hasattr(self, "worker_thread") and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

    def on_reset_clicked(self):
        self.on_stop_clicked()
        self.graph_template.plot.clear()
        pen = pg.mkPen(color=self.pen_color, width=self.pen_width)
        self.curve = self.graph_template.plot.plot([], [], pen=pen, name=self.signal_name)
        self.setup_worker()

    def apply_zoom(self, zoom_in: bool):
        factor = 0.5 if zoom_in else 2
        mode = self.zoom_combo_box.currentText()

        plot_widget = self.graph_template.plot
        x_range, y_range = plot_widget.viewRange()
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2

        if mode in ["X Axis", "Both"]:
            width = (x_range[1] - x_range[0]) * factor
            plot_widget.setXRange(x_center - width / 2, x_center + width / 2)
        if mode in ["Y Axis", "Both"]:
            height = (y_range[1] - y_range[0]) * factor
            plot_widget.setYRange(y_center - height / 2, y_center + height / 2)

    def zoom_in(self):
        self.apply_zoom(True)

    def zoom_out(self):
        self.apply_zoom(False)

    def auto_scale(self):
        plot_widget = self.graph_template.plot
        plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def select_folder(self):
        destination_dir = QFileDialog.getExistingDirectory()
        if destination_dir:
            self.destination.setText(destination_dir)
            self.destination.setToolTip(f"Selected: {destination_dir}")

    def on_start_logging(self):
        print("Logging started ")
        folder = self.destination.text()
        if not folder:
            QMessageBox.warning(self, "Warning", "Please select a destination folder.")
            return

        log_type = self.logger_combo_box.currentText()
        if log_type == "Select format":
            QMessageBox.warning(self, "Warning", "Please choose a log format")
            return

        file_path = os.path.join(folder, f"{self.signal_name}.csv")

        if log_type == "CSV":
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                headers = ["Time (s)", "Amplitude"]
                csv_writer.writerow(headers)

            self.logger = DataLogger(curve=self.curve, signal_name=self.signal_name, directory=folder)
            self.is_logging = True #flag true so data will be logging
            self.logging_timer.start()

        elif log_type == "Binary":
            with open(file_path, 'w', newline='') as binfile:
                headers = ["Time (s)", "Amplitude"]
                binfile.write(struct.pack('dd',headers))

            self.logger = DataLogger(curve=self.curve, signal_name=self.signal_name, directory=folder)
            self.is_logging = True  # flag true so data will be logging
            self.logging_timer.start()

        self.stop_log_btn.setEnabled(True)
        self.start_log_btn.setEnabled(False)

    def on_stop_logging(self):
        print("Logging stopped ")
        self.is_logging = False
        self.stop_log_btn.setEnabled(False)
        self.start_log_btn.setEnabled(True)
        self.logging_timer.stop()
        print(f"Logged file is saved to: {self.destination.text()} as {self.logger_combo_box.currentText()} file ")

    def eventFilter(self, obj, event):
        if obj == self.destination and event.type() == QEvent.MouseButtonPress:
            self.select_folder()
            return True
        return super().eventFilter(obj, event)