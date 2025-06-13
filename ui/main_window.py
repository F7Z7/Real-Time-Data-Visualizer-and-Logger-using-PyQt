import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QFrame, QCheckBox, QComboBox, QSplitter, QLineEdit,QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QThread
import pyqtgraph as pg
from src.data_worker import DataWorker
from src.plotting import sine_graph, cos_graph


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Visualiser")
        self.setMinimumSize(1100, 1100)

        # Init State
        self.phase = 0
        self.t = 0
        self.dt = 0.05
        self.x, self.sine_data, self.cos_data = [], [], []
        self.max_points = 200

        # UI Setup
        self.initUI()

        # Worker Thread
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.worker_thread.started.connect(self.worker.start_work)
        self.destroyed.connect(self.clean_up_worker)


    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # === Left: Controls Panel ===
        self.control_panel = self.setup_controls()
        main_layout.addWidget(self.control_panel)

        # === Right: Graph Area ===
        self.setup_plots()
        graphLayout = QVBoxLayout()
        graphLayout.setSpacing(15)

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            graphLayout.addWidget(plot)

        graph_container = QWidget()
        graph_container.setLayout(graphLayout)
        main_layout.addWidget(graph_container)

    def setup_controls(self):
        control_layout = QVBoxLayout()
        control_layout.setSpacing(5)  # Equal spacing between elements
        control_layout.setContentsMargins(5, 5,5,5)
        control_layout.setAlignment(Qt.AlignTop)
        # --- Buttons ---
        buttons = [
            ("Start", self.on_click_start),
            ("Stop", self.on_click_stop),
            ("Reset", self.reset_plot),
            ("Zoom In", self.zoom_in),
            ("Zoom Out", self.zoom_out),
            ("Auto-Scale", self.auto_scale)
        ]

        for label, slot in buttons:
            btn = QPushButton(label)
            btn.setFixedSize(120, 30)
            btn.clicked.connect(slot)
            control_layout.addWidget(btn)

        # --- Zoom Mode ComboBox ---
        zoom_label = QLabel("Zoom Mode")
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setCurrentIndex(2)

        control_layout.addWidget(zoom_label)
        control_layout.addWidget(self.zoom_combo_box)

        # --- Input Method Selection ---
        input_label = QLabel("Input Preferred Method")
        self.input_method = QComboBox()
        self.input_method.addItems(["Select type of input", "User Defined Signals", "Pre Defined Signals"])
        self.input_method.setCurrentIndex(0)
        self.input_method.currentIndexChanged.connect(self.handle_input_change)

        control_layout.addWidget(input_label)
        control_layout.addWidget(self.input_method)

        # --- Placeholder for Dynamic Input Fields ---
        self.user_input_layout = QVBoxLayout()
        self.user_input_layout.setSpacing(5)
        control_layout.addLayout(self.user_input_layout)

        # --- Signal Visibility Checkboxes ---
        self.choices = ["Show Signal A", "Show Signal B", "Show X-Y Plot"]
        self.signal_check = []

        for text in self.choices:
            cb = QCheckBox(text)
            cb.setChecked(True)
            self.signal_check.append(cb)
            control_layout.addWidget(cb)

        self.signal_check[0].stateChanged.connect(self.toggle_visbile_signA)
        self.signal_check[1].stateChanged.connect(self.toggle_visbile_signB)
        self.signal_check[2].stateChanged.connect(self.toggle_visbile_x_y_plot)

        # Finalize
        container = QWidget()
        container.setLayout(control_layout)
        container.setFixedWidth(200)
        return container

    def setup_plots(self):
        # --- Plot 1: Sine ---
        self.plot_widget1 = pg.PlotWidget()
        self.plot_widget1.setBackground('w')
        self.plot_widget1.setFixedHeight(300)
        self.plot_widget1.showGrid(x=True, y=True)
        self.plot_widget1.addLegend()
        self.sine_curve = self.plot_widget1.plot(pen=pg.mkPen('r', width=5), name="Sine", antialias=True)

        # --- Plot 2: Cosine ---
        self.plot_widget2 = pg.PlotWidget()
        self.plot_widget2.setBackground('w')
        self.plot_widget2.setFixedHeight(300)
        self.plot_widget2.showGrid(x=True, y=True)
        self.plot_widget2.addLegend()
        self.cos_curve = self.plot_widget2.plot(pen=pg.mkPen('b', width=5), name="Cosine", antialias=True)

        # --- Plot 3: X vs Y ---
        self.plot_widget3 = pg.PlotWidget()
        self.plot_widget3.setBackground('w')
        self.plot_widget3.setFixedHeight(300)
        self.plot_widget3.showGrid(x=True, y=True)
        self.plot_widget3.addLegend()
        self.x_y_plot = self.plot_widget3.plot(pen=pg.mkPen('#ff32cc', width=5), name="X vs Y", antialias=True)

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setContentsMargins(5, 5, 5, 5)
            plot.setLabel("bottom", "Time", units='sec', **{'color': 'black', "font-size": "10pt"})
            plot.setLabel("left", "Amplitude", **{'color': 'black', "font-size": "10pt"})
            plot.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        self.plot_widget3.setLabel("left", "Cos(t)", **{'color': 'blue', "font-size": "10pt"})
        self.plot_widget3.setLabel("bottom", "Sin(t)", **{'color': 'red', "font-size": "10pt"})

    # -------------------------
    # Worker Handling
    # -------------------------
    def on_click_start(self):
        if not self.worker_thread.isRunning():
            self.worker_thread.start()

    def on_click_stop(self):
        self.worker.stop_work()
        self.worker_thread.quit()
        self.worker_thread.wait()

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

    #plot updation
    def update_plot(self, t, sin, cos):
        self.x.append(t)
        self.sine_data.append(sin)
        self.cos_data.append(cos)

        if len(self.x) > self.max_points:
            self.x.pop(0)
            self.sine_data.pop(0)
            self.cos_data.pop(0)

        self.sine_curve.setData(self.x, self.sine_data)
        self.cos_curve.setData(self.x, self.cos_data)
        self.x_y_plot.setData(self.sine_data, self.cos_data)

        if self.zoom_combo_box.currentText() not in ["X Axis", "Both"]:
            self.plot_widget1.setXRange(self.t - 10, self.t)
            self.plot_widget2.setXRange(self.t - 10, self.t)

    def reset_plot(self):
        self.timer.stop()
        self.t = 0
        self.x.clear()
        self.sine_data.clear()
        self.cos_data.clear()
        self.sine_curve.clear()
        self.cos_curve.clear()
        self.x_y_plot.clear()

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setXRange(0, 10)
            plot.setYRange(-1, 1)

#zooming
    def apply_zoom(self, zoom_in: bool):
        factor = 0.5 if zoom_in else 2
        mode = self.zoom_combo_box.currentText()
        for plot_widget in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
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
        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    # -------------------------
    # Visibility Toggles
    # -------------------------
    def toggle_visbile_signA(self, state):
        self.sine_curve.setVisible(state == Qt.Checked)

    def toggle_visbile_signB(self, state):
        self.cos_curve.setVisible(state == Qt.Checked)

    def toggle_visbile_x_y_plot(self, state):
        self.x_y_plot.setVisible(state == Qt.Checked)

    # -------------------------
    # Input Method Handling
    # -------------------------
    def handle_input_change(self):
        while self.user_input_layout.count():
            child = self.user_input_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.input_method.currentText() == "User Defined Signals":
            self.input_1 = QLineEdit()
            self.label_1 = QLabel("Input 1:")
            self.input_2 = QLineEdit()
            self.label_2 = QLabel("Input 2:")
            for label, box in [(self.label_1, self.input_1), (self.label_2, self.input_2)]:
                self.user_input_layout.addWidget(label)
                self.user_input_layout.addWidget(box)

        elif self.input_method.currentText() == "Pre Defined Signals":
            user_input = QComboBox()
            user_input.addItems(["Sine", "Cos", "Tan", "Cot", "Sec", "Cosec"])
            self.user_input_layout.addWidget(user_input)
