# === graph_widget.py ===
import csv
import os
import random
import struct

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QSizePolicy, QGroupBox, QSpacerItem, QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QThread, Qt, QEvent, QTimer, QCoreApplication
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
        self.logging_timer = QTimer()
        self.logging_timer.setInterval(500)
        self.logging_timer.timeout.connect(self.log_periodically)

    def log_periodically(self):
        if self.is_logging and self.logger:
            if self.log_format== "CSV":
                self.logger.logg_csv()
            elif self.log_format == "Binary":
                self.logger.logg_binary()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.create_graph_section(main_layout)
        self.create_control_panel(main_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_graph_section(self, parent_layout):
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
        controls_box = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        controls_layout.setContentsMargins(15, 15, 15, 15)
        # self.create_playback_controls(controls_layout)
        # self.add_vertical_separator(controls_layout)
        # self.create_zoom_controls(controls_layout)
        # self.add_vertical_separator(controls_layout)
        # self.create_logging_controls(controls_layout)
        self.create_range_controls(controls_layout)
        controls_box.setLayout(controls_layout)
        parent_layout.addWidget(controls_box)

    # def create_playback_controls(self, parent_layout):
    #     playback_group = QGroupBox("Playback")
    #     playback_group.setVisible(False)  # hide individual controls
    #     layout = QVBoxLayout()
    #     for label in ["Start", "Stop", "Reset"]:
    #         btn = QPushButton(label)
    #         btn.setFixedSize(100, 30)
    #         layout.addWidget(btn)
    #     playback_group.setLayout(layout)
    #     parent_layout.addWidget(playback_group)

    # def create_zoom_controls(self, parent_layout):
    #     group = QGroupBox("Zoom & Scale")
    #     parent_zoom = QHBoxLayout()
    #     layout = QVBoxLayout()
    #
    #     axis_layout = QHBoxLayout()
    #     axis_layout.addWidget(QLabel("Axis:"))
    #     self.zoom_combo_box = QComboBox()
    #     self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
    #     self.zoom_combo_box.setFixedWidth(80)
    #     axis_layout.addWidget(self.zoom_combo_box)
    #     axis_layout.addStretch()
    #     layout.addLayout(axis_layout)
    #
    #     for text, method in [("＋ Zoom In", self.zoom_in), ("－ Zoom Out", self.zoom_out), ("Auto Scale", self.auto_scale)]:
    #         btn = QPushButton(text)
    #         btn.setFixedSize(100, 30)
    #         btn.clicked.connect(method)
    #         layout.addWidget(btn)
    #
    #     parent_zoom.addLayout(layout)
    def create_range_controls(self, parent_layout):
        group = QGroupBox("Zoom Range & Amplitude")
        range_layout = QVBoxLayout()
        for label_text, placeholder in {
            "Enter desired range": "e.g. 1-10s",
            "Enter desired amplitude": "e.g. -1 to 1"
        }.items():
            range_layout.addWidget(QLabel(label_text))
            le = QLineEdit()
            le.setPlaceholderText(placeholder)
            range_layout.addWidget(le)
        group.setLayout(range_layout)
        parent_layout.addWidget(group)

    # def create_logging_controls(self, parent_layout):
    #     group = QGroupBox("Data Logging")
    #     layout = QVBoxLayout()
    #
    #     format_layout = QHBoxLayout()
    #     format_layout.addWidget(QLabel("Format:"))
    #     self.logger_combo_box = QComboBox()
    #     self.logger_combo_box.addItems(["Select format", "CSV", "Binary"])
    #     self.logger_combo_box.setFixedWidth(100)
    #     format_layout.addWidget(self.logger_combo_box)
    #     format_layout.addStretch()
    #     layout.addLayout(format_layout)
    #
    #     size_layout = QHBoxLayout()
    #     size_layout.addWidget(QLabel("Max Size:"))
    #     self.size_combo = QComboBox()
    #     self.size_combo.addItems(["1MB", "5MB", "10MB", "50MB", "100MB"])
    #     self.size_combo.setFixedWidth(100)
    #     size_layout.addWidget(self.size_combo)
    #     size_layout.addStretch()
    #     layout.addLayout(size_layout)
    #
    #     folder_layout = QVBoxLayout()
    #     folder_layout.addWidget(QLabel("Destination:"))
    #     self.destination = QLineEdit()
    #     self.destination.setReadOnly(True)
    #     self.destination.setFixedWidth(200)
    #     self.destination.setPlaceholderText("Click to select folder...")
    #     self.destination.setCursor(Qt.PointingHandCursor)
    #     folder_layout.addWidget(self.destination)
    #     layout.addLayout(folder_layout)
    #
    #     btn_layout = QHBoxLayout()
    #     self.start_log_btn = QPushButton("Start Log")
    #     self.stop_log_btn = QPushButton("Stop Log")
    #     self.stop_log_btn.setEnabled(False)
    #     self.start_log_btn.setFixedSize(90, 30)
    #     self.stop_log_btn.setFixedSize(90, 30)
    #     self.start_log_btn.clicked.connect(self.start_logging)
    #     self.stop_log_btn.clicked.connect(self.stop_logging)
    #     btn_layout.addWidget(self.start_log_btn)
    #     btn_layout.addWidget(self.stop_log_btn)
    #     layout.addLayout(btn_layout)
    #
    #     group.setLayout(layout)
    #     parent_layout.addWidget(group)

    def add_vertical_separator(self, layout):
        layout.addItem(QSpacerItem(1, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def generate_color(self):
        return "#" + "".join(random.choice('0123456789ABCDEF') for _ in range(6))

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

    def start_plot(self):
        if not self.worker_thread.isRunning():
            self.worker_thread.started.connect(self.worker.start_work)
            self.worker_thread.start()

    def stop_plot(self):
        if self.worker:
            self.worker.stop_work()
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

    def reset_plot(self):
        self.stop_plot()
        self.graph_template.plot.clear()

        # Force event processing to ensure disconnects complete
        QCoreApplication.processEvents()

        # Recreate the curve
        pen = pg.mkPen(color=self.pen_color, width=self.pen_width)
        self.curve = self.graph_template.plot.plot([], [], pen=pen, name=self.signal_name)

        # Delay a bit to ensure old worker is shut down before starting a new one
        QTimer.singleShot(0, self.setup_worker)

    def zoom_in_all(self,zoom_mode):
        self.apply_zoom(True,zoom_mode)

    def zoom_out_all(self,zoom_mode):
        self.apply_zoom(False,zoom_mode)

    def auto_scale(self):
        self.graph_template.plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def apply_zoom(self, zoom_in, zoom_mode):
        factor = 0.5 if zoom_in else 2
        pw = self.graph_template.plot
        x_range, y_range = pw.viewRange()
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2

        if zoom_mode in ["X Axis", "Both"]:
            width = (x_range[1] - x_range[0]) * factor
            pw.setXRange(x_center - width/2, x_center + width/2)
        if zoom_mode in ["Y Axis", "Both"]:
            height = (y_range[1] - y_range[0]) * factor
            pw.setYRange(y_center - height/2, y_center + height/2)

    def start_logging(self,destinaion,max_file_size,log_format):
        self.folder=destinaion
        self.log_format = log_format
        if not self.folder:
            QMessageBox.warning(self, "Warning", "Please select a destination folder.")
            return

        if self.log_format == "Select format":
            QMessageBox.warning(self, "Warning", "Please choose a log format")
            return

        file_path = os.path.join(self.folder, f"{self.signal_name}_{self.graph_id}.csv")

        self.logger = DataLogger(curve=self.curve, signal_name=self.signal_name, directory=self.folder)
        self.is_logging = True
        self.logging_timer.start()

    def stop_logging(self):
        self.is_logging = False
        self.logging_timer.stop()
        print(f"Log saved in {self.folder} as {self.log_format}")



