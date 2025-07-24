# === graph_widget.py ===
import csv
import os
import random
import struct

import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QSizePolicy, QGroupBox, QSpacerItem, QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QThread, Qt, QEvent, QTimer, QCoreApplication
import pyqtgraph as pg
from graph_plotting_functionalities.AxisRangeDialog import AxisRangeDialog
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
    def __init__(self, graph_id, graph_manager,mode="operation", signal1="Sin", signal2="Cos", num=1):
        super().__init__()
        self.file_size = None
        self.graph_id = graph_id
        self.mode = mode
        self.signal_name = signal1
        self.signal_func = Signal_list[signal1]
        self.dt = 0.05
        self.graph_manager = graph_manager
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

        self.dialog= AxisRangeDialog()
        self.graph_template.plot.scene().sigMouseClicked.connect(self.on_plot_clicked) #this for so that the diaolgue box appaers when the clicked on the plot
#for opeartion tabs
        self.is_Math=False
        self.math_input1 = None
        self.math_input2 = None
        self.math_operation = None
        self.math_constant = None

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
        # self.create_range_controls(controls_layout)
        # controls_box.setLayout(controls_layout)
        # parent_layout.addWidget(controls_box)

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
#     def create_range_controls(self, parent_layout):
#         group = QGroupBox("Zoom Range & Amplitude")
#         range_amplitude_layout = QVBoxLayout()
# #x axis setting
#         range_layout = QVBoxLayout()
#         range_layout.addWidget(QLabel("Enter Desired Range: -10s to 10s"))
#
#         range_input_line_edit_layout = QHBoxLayout()
#         self.range_from_input = QLineEdit()
#         self.range_from_input.setPlaceholderText("From")
#         self.range_to_input = QLineEdit()
#         self.range_to_input.setPlaceholderText("To")
#
#         for line_edit in [self.range_from_input, self.range_to_input]:
#             range_input_line_edit_layout.addWidget(line_edit)
#
#         range_layout.addLayout(range_input_line_edit_layout)
# #yaxis setting
#         amplitude_layout = QVBoxLayout()
#         amplitude_layout.addWidget(QLabel("Enter Desired Amplitude: -1 to 1"))
#
#         amplitude_input_line_edit_layout = QHBoxLayout()
#         self.amplitude_from_input = QLineEdit()
#         self.amplitude_from_input.setPlaceholderText("From")
#         self.amplitude_to_input = QLineEdit()
#         self.amplitude_to_input.setPlaceholderText("To")
#
#         for line_edit in [self.amplitude_from_input, self.amplitude_to_input]:
#             amplitude_input_line_edit_layout.addWidget(line_edit)
#
#         amplitude_layout.addLayout(amplitude_input_line_edit_layout)
#
#        #combining both
#         for layout in [range_layout, amplitude_layout]:
#             range_amplitude_layout.addLayout(layout)
#         reformat_btn=QPushButton("Reformat the axes")
#         reformat_btn.clicked.connect(self.on_reformat_clicked)
#         range_amplitude_layout.addWidget(reformat_btn)
#         group.setLayout(range_amplitude_layout)
#         group.setEnabled(False)
#         parent_layout.addWidget(group)
#         parent_layout.setEnabled(False)


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
        t = np.asarray(t).flatten()
        y1 = np.asarray(y1).flatten()

        if t.shape != y1.shape:
            print(f"[ERROR] Shape mismatch: t.shape = {t.shape}, y1.shape = {y1.shape}")
            return  # Or handle accordingly (e.g., pad/crop the shorter one)

        self.curve.setData(t, y1)
    def start_plot(self):
        if self.is_Math:
            self.math_plot()
        else:
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

    def start_logging(self,destinaion,max_file_size,log_format,create_new_file:bool):
        self.folder=destinaion
        self.log_format = log_format
        if not self.folder:
            QMessageBox.warning(self, "Warning", "Please select a destination folder.")
            return

        if self.log_format == "Select format":
            QMessageBox.warning(self, "Warning", "Please choose a log format")
            return

        file_path = os.path.join(self.folder, f"{self.signal_name}_{self.graph_id}.csv")
        self.file_size=max_file_size
        self.logger = DataLogger(curve=self.curve, signal_name=self.signal_name, directory=self.folder,max_file_size=self.file_size,new_file=create_new_file)
        self.is_logging = True
        self.logging_timer.start()

    def stop_logging(self):
        self.is_logging = False
        self.logging_timer.stop()
        print(f"Log saved in {self.folder} as {self.log_format}")
    def on_plot_clicked(self,event):
        if event.button() == Qt.RightButton:
            print("right click detected")
            self.on_reformat_clicked()
    def on_reformat_clicked(self):
        view_range=self.graph_template.plot.viewRange()
        self.dialog.set_fields(view_range)
        if self.dialog.exec_()==self.dialog.Accepted:
            print("function didn reach here")
            x_min, x_max, y_min, y_max = self.dialog.get_ranges()
            self.graph_template.plot.setXRange(x_min, x_max)
            self.graph_template.plot.setYRange(y_min, y_max)

    def set_as_math_expression(self, input1, input2, operation, constant=None):
        self.is_math = True
        self.math_input1 = input1
        self.math_input2 = input2
        self.math_operation = operation
        self.math_constant = constant

    def compute_math_expression(self,y1,y2):
        operation = self.math_operation
        try:
            if operation == "A + B":
                result_y = y1 + y2
            elif operation == "A - B":
                result_y = y1 - y2
            elif operation == "A * B":
                result_y = y1 * y2
            elif operation == "A / B":
                result_y = y1 / y2
            elif operation == "sin(A)":
                result_y = np.sin(y1)
            elif operation == "cos(B)":
                result_y = np.cos(y2)
            elif operation == "sin(A) + 2*B":
                result_y = np.sin(y1) + 2 * y2
            else:
                print("Unsupported operation:", operation)
                return
        except Exception as e:
            print("Error during math computation:", e)
            return

    def math_plot(self):
        try:
            x1, y1 = self.graph_manager.get_signal_data_by_name(self.math_input1)
            x2, y2 = self.graph_manager.get_signal_data_by_name(self.math_input2)
        except Exception:
            x1 = y1 = x2 = y2 = None

        if None in (x1, y1, x2, y2):
            print(f"[INFO] Waiting for input signals to be ready for math graph {self.graph_id}...")
            QTimer.singleShot(500, self.math_plot)
            return

        if len(y1) != len(y2):
            print(f"[ERROR] Signal lengths do not match for Graph {self.graph_id}")
            return

        try:
            result_y = self.compute_math_expression(y1, y2)
            self.update_plot(x1, result_y)
        except Exception as e:
            print(f"[ERROR] Math computation failed for Graph {self.graph_id}: {e}")

        # Create new signal/graph

