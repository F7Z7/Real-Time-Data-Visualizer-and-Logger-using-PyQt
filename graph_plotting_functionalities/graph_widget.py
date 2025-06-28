import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QSizePolicy, QGroupBox, QSpacerItem, QLineEdit, QFileDialog
)
from PyQt5.QtCore import QThread, Qt, QEvent
import pyqtgraph as pg

from graph_plotting_functionalities.plotting import Signal_list
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

        self.initUI()
        self.setup_worker()

        self.destination.installEventFilter(self)
    def initUI(self):
        layout = QVBoxLayout()

        # === Graph ===
        self.graph_template = GraphTemplate(
            title=f"Graph {self.graph_id}",
            xlabel="Time (s)",
            ylabel="Amplitude",
            legend=True,
        )
        self.graph_template.plot.enableAutoRange(False)
        pen = pg.mkPen(color=self.pen_color, width=self.pen_width)
        self.curve = self.graph_template.plot.plot([], [], pen=pen, name=self.signal_name)
        layout.addWidget(self.graph_template)

        # === Control Panel ===
        controls_box = QGroupBox("Controls")
        controls_layout = QHBoxLayout()

        # --- Start/Stop/Reset Buttons ---
        button_layout = QVBoxLayout()
        self.start_btn = QPushButton('Start')
        self.stop_btn = QPushButton('Stop')
        self.reset_btn = QPushButton('Reset')
        for btn in [self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setFixedSize(100, 30)
            button_layout.addWidget(btn)

        self.start_btn.setToolTip("Start signal plotting")
        self.stop_btn.setToolTip("Stop signal plotting")
        self.reset_btn.setToolTip("Clear and restart the plot")

        # --- Zoom Controls ---
        zoom_layout = QVBoxLayout()
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setFixedWidth(100)
        self.zoom_combo_box.setToolTip("Choose axis to zoom")

        self.zoom_in_btn = QPushButton('＋ Zoom In')
        self.zoom_out_btn = QPushButton('－ Zoom Out')
        self.auto_scale_btn = QPushButton('Auto-scale')

        for widg in [self.zoom_in_btn, self.zoom_out_btn, self.auto_scale_btn]:
            widg.setFixedSize(100, 30)

        self.zoom_in_btn.setToolTip("Zoom in the selected axis")
        self.zoom_out_btn.setToolTip("Zoom out the selected axis")
        self.auto_scale_btn.setToolTip("Automatically scale plot to fit data")

        zoom_layout.addWidget(self.zoom_combo_box)
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.auto_scale_btn)
        zoom_layout.addStretch()

        # === Logger Layout ===
        # File format selection

        logger_layout = QVBoxLayout()

        # === File Format Selection ===
        logger_combo_row = QHBoxLayout()
        format_label = QLabel("Choose File Format")
        self.logger_combo_box = QComboBox()
        self.logger_combo_box.addItems(["Select the format", "CSV", "Binary"])
        self.logger_combo_box.setToolTip("Select file format for data logging")
        logger_combo_row.addWidget(format_label)
        logger_combo_row.addSpacing(10)
        logger_combo_row.addWidget(self.logger_combo_box)
        logger_combo_row.addStretch(1)  # Add right spacing
        logger_layout.addLayout(logger_combo_row)

        # === Max File Size Selection ===
        size_selection_layout = QHBoxLayout()
        size_selection_layout.addWidget(QLabel("Choose Max File Size"))

        self.size_combo = QComboBox()
        self.size_combo.addItems(["1MB", "5MB", "10MB", "50MB", "100MB"])
        self.size_combo.setFixedWidth(100)
        self.size_combo.setToolTip("Max size for each log file")
        size_selection_layout.addSpacing(10)
        size_selection_layout.addWidget(self.size_combo)
        size_selection_layout.addStretch(1)
        logger_layout.addLayout(size_selection_layout)

        # === Destination Folder Selection ===
        folder_combo_layout = QVBoxLayout()
        folder_combo_layout.addWidget(QLabel("Choose Destination Folder"))

        self.destination = QLineEdit()
        self.destination.setReadOnly(True)
        self.destination.setFixedWidth(250)
        self.destination.setPlaceholderText("Click here to select folder...")
        self.destination.setCursor(Qt.PointingHandCursor)
        folder_combo_layout.addSpacing(10)
        folder_combo_layout.addWidget(self.destination)
        folder_combo_layout.addStretch(1)
        logger_layout.addLayout(folder_combo_layout)



        # === Logging Buttons ===
        logger_button_row = QHBoxLayout()
        logger_buttons = [("Start Logging", self.on_start_logging), ("Stop Logging", self.on_stop_logging)]
        for text, func in logger_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            btn.setFixedSize(120, 30)
            logger_button_row.addWidget(btn)
        logger_button_row.addStretch(1)
        logger_layout.addLayout(logger_button_row)

        # Add to controls layout
        controls_layout.addLayout(button_layout)
        # controls_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        controls_layout.addLayout(zoom_layout)
        # controls_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        controls_layout.addLayout(logger_layout)

        controls_box.setLayout(controls_layout)
        layout.addWidget(controls_box)
        layout.addStretch()
        self.setLayout(layout)

        # Connections
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.auto_scale_btn.clicked.connect(self.auto_scale)

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

    def on_start_logging(self):
        # Placeholder: implement logging start
        print("Start logging clicked")
        return 0

    def on_stop_logging(self):
        # Placeholder: implement logging stop
        print("Stop logging clicked")
        return 0

    def select_folder(self):
        destination_dir = QFileDialog.getExistingDirectory()
        if destination_dir:
            self.destination.setText(destination_dir)
            self.destination.setToolTip(f"Selected: {destination_dir}")


    def eventFilter(self, obj,event):
        if obj==self.destination and event.type()==QEvent.MouseButtonPress:
            self.select_folder()
            return True

        return super().eventFilter(obj, event)
