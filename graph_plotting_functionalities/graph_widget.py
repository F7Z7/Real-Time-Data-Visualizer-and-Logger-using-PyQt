# === graph_widget.py ===
import csv
import os
import random
import struct

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QSizePolicy, QGroupBox, QSpacerItem, QLineEdit, QFileDialog, QMessageBox
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
            if self.logger_combo_box.currentText() == "CSV":
                self.logger.logg_csv()
            elif self.logger_combo_box.currentText() == "Binary":
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
        self.create_playback_controls(controls_layout)
        self.add_vertical_separator(controls_layout)
        self.create_zoom_controls(controls_layout)
        self.add_vertical_separator(controls_layout)
        self.create_logging_controls(controls_layout)
        controls_box.setLayout(controls_layout)
        parent_layout.addWidget(controls_box)

    def create_playback_controls(self, parent_layout):
        playback_group = QGroupBox("Playback")
        playback_group.setVisible(False)  # hide individual controls
        layout = QVBoxLayout()
        for label in ["Start", "Stop", "Reset"]:
            btn = QPushButton(label)
            btn.setFixedSize(100, 30)
            layout.addWidget(btn)
        playback_group.setLayout(layout)
        parent_layout.addWidget(playback_group)

    def create_zoom_controls(self, parent_layout):
        group = QGroupBox("Zoom & Scale")
        parent_zoom = QHBoxLayout()
        layout = QVBoxLayout()

        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("Axis:"))
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setFixedWidth(80)
        axis_layout.addWidget(self.zoom_combo_box)
        axis_layout.addStretch()
        layout.addLayout(axis_layout)

        for text, method in [("＋ Zoom In", self.zoom_in), ("－ Zoom Out", self.zoom_out), ("Auto Scale", self.auto_scale)]:
            btn = QPushButton(text)
            btn.setFixedSize(100, 30)
            btn.clicked.connect(method)
            layout.addWidget(btn)

        parent_zoom.addLayout(layout)

        input_range = QVBoxLayout()
        for label_text, placeholder in {"Enter desired range": "e.g. 1-10s", "Enter desired amplitude": "e.g. -1 to 1"}.items():
            input_range.addWidget(QLabel(label_text))
            le = QLineEdit()
            le.setPlaceholderText(placeholder)
            input_range.addWidget(le)

        parent_zoom.addLayout(input_range)
        group.setLayout(parent_zoom)
        parent_layout.addWidget(group)

    def create_logging_controls(self, parent_layout):
        group = QGroupBox("Data Logging")
        layout = QVBoxLayout()

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.logger_combo_box = QComboBox()
        self.logger_combo_box.addItems(["Select format", "CSV", "Binary"])
        self.logger_combo_box.setFixedWidth(100)
        format_layout.addWidget(self.logger_combo_box)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1MB", "5MB", "10MB", "50MB", "100MB"])
        self.size_combo.setFixedWidth(100)
        size_layout.addWidget(self.size_combo)
        size_layout.addStretch()
        layout.addLayout(size_layout)

        folder_layout = QVBoxLayout()
        folder_layout.addWidget(QLabel("Destination:"))
        self.destination = QLineEdit()
        self.destination.setReadOnly(True)
        self.destination.setFixedWidth(200)
        self.destination.setPlaceholderText("Click to select folder...")
        self.destination.setCursor(Qt.PointingHandCursor)
        folder_layout.addWidget(self.destination)
        layout.addLayout(folder_layout)

        btn_layout = QHBoxLayout()
        self.start_log_btn = QPushButton("Start Log")
        self.stop_log_btn = QPushButton("Stop Log")
        self.stop_log_btn.setEnabled(False)
        self.start_log_btn.setFixedSize(90, 30)
        self.stop_log_btn.setFixedSize(90, 30)
        self.start_log_btn.clicked.connect(self.start_logging)
        self.stop_log_btn.clicked.connect(self.stop_logging)
        btn_layout.addWidget(self.start_log_btn)
        btn_layout.addWidget(self.stop_log_btn)
        layout.addLayout(btn_layout)

        group.setLayout(layout)
        parent_layout.addWidget(group)

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
        pen = pg.mkPen(color=self.pen_color, width=self.pen_width)
        self.curve = self.graph_template.plot.plot([], [], pen=pen, name=self.signal_name)
        self.setup_worker()

    def zoom_in(self):
        self.apply_zoom(True)

    def zoom_out(self):
        self.apply_zoom(False)

    def auto_scale(self):
        self.graph_template.plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def apply_zoom(self, zoom_in):
        factor = 0.5 if zoom_in else 2
        mode = self.zoom_combo_box.currentText()
        pw = self.graph_template.plot
        x_range, y_range = pw.viewRange()
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2

        if mode in ["X Axis", "Both"]:
            width = (x_range[1] - x_range[0]) * factor
            pw.setXRange(x_center - width/2, x_center + width/2)
        if mode in ["Y Axis", "Both"]:
            height = (y_range[1] - y_range[0]) * factor
            pw.setYRange(y_center - height/2, y_center + height/2)

    def start_logging(self):
        folder = self.destination.text()
        if not folder:
            QMessageBox.warning(self, "Warning", "Please select a destination folder.")
            return

        log_type = self.logger_combo_box.currentText()
        if log_type == "Select format":
            QMessageBox.warning(self, "Warning", "Please choose a log format")
            return

        file_path = os.path.join(folder, f"{self.signal_name}_{self.graph_id}.csv")

        if log_type == "CSV":
            with open(file_path, 'w', newline='') as f:
                csv.writer(f).writerow(["Time (s)", "Amplitude"])
        elif log_type == "Binary":
            with open(file_path, 'wb') as f:
                f.write(struct.pack('2d', 0.0, 0.0))  # placeholder

        self.logger = DataLogger(curve=self.curve, signal_name=self.signal_name, directory=folder)
        self.is_logging = True
        self.logging_timer.start()
        self.start_log_btn.setEnabled(False)
        self.stop_log_btn.setEnabled(True)

    def stop_logging(self):
        self.is_logging = False
        self.logging_timer.stop()
        self.start_log_btn.setEnabled(True)
        self.stop_log_btn.setEnabled(False)
        print(f"Log saved in {self.destination.text()} as {self.logger_combo_box.currentText()}")

    def start_log(self):
        self.start_logging()

    def stop_logg(self):
        self.stop_logging()

    def eventFilter(self, obj, event):
        if obj == self.destination and event.type() == QEvent.MouseButtonPress:
            self.select_folder()
            return True
        return super().eventFilter(obj, event)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory()
        if folder:
            self.destination.setText(folder)
            self.destination.setToolTip(f"Selected: {folder}")
