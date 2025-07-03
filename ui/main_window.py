# === main_window.py ===
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QComboBox, QLineEdit, QMessageBox, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QThread
import numpy as np
import pyqtgraph as pg

from src.data_worker import DataWorker
from src.math_functions import compute_expression
from graph_plotting_functionalities.Graph_Layout import Generate_Graph
from graph_plotting_functionalities.graph_widget import create_button_row


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Visualiser")
        self.setMinimumSize(1100, 1100)

        self.phase = 0
        self.t = 0
        self.dt = 0.05
        self.x, self.signal1_data, self.signal2_data = [], [], []
        self.max_points = 200

        self.initUI()
        self.setup_worker()

        self.plot_start = False
        self.plot_stop = False
        self.is_reset = False

        pg.setConfigOptions(antialias=True)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        self.control_panel = self.setup_controls()
        main_layout.addWidget(self.control_panel)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        self.generate_graph_widget = Generate_Graph()
        right_layout.addWidget(self.generate_graph_widget)

        main_layout.addLayout(right_layout)

    def setup_controls(self):
        control_layout = QVBoxLayout()
        control_layout.setSpacing(5)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setAlignment(Qt.AlignTop)

        user_input_layout = QVBoxLayout()
        self.user_input1 = QComboBox()
        self.user_input2 = QComboBox()
        signals = [
            "Select a Signal",
            "Sin", "Cos", "Tan", "Cosec",
            "Sec", "Cot", "Triangle", "Square"
        ]
        self.user_input1.addItems(signals)
        self.user_input2.addItems(signals)

        for label, box in [("Signal A", self.user_input1), ("Signal B", self.user_input2)]:
            user_input_layout.addWidget(QLabel(label))
            user_input_layout.addWidget(box)

        control_layout.addLayout(user_input_layout)

        math_layout = QVBoxLayout()
        math_layout.addWidget(QLabel("Math Operation Selection"))
        self.operations = QComboBox()
        self.operations.addItems([
            "Choose an operation", "A + B", "A - B", "A * B", "A / B",
            "sin(A)", "cos(B)", "sin(A) + 2*B"
        ])
        math_layout.addWidget(self.operations)

        math_layout.addWidget(QLabel("Optional Constants"))
        self.constant_input = QLineEdit()
        self.constant_input.setPlaceholderText("eg: 2, 1.5")
        math_layout.addWidget(self.constant_input)

        self.preview_btn = QPushButton("Preview the expression")
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        math_layout.addWidget(self.preview_btn)

        math_layout.addWidget(QLabel("Preview"))
        self.preview_input = QLineEdit()
        self.preview_input.setEnabled(False)
        math_layout.addWidget(self.preview_input)

        self.calculate_btn = QPushButton("Calculate and Plot")
        self.calculate_btn.clicked.connect(self.on_calculate_plot)
        math_layout.addWidget(self.calculate_btn)

        control_layout.addLayout(math_layout)

        # Global Buttons
        button_groups = [
            [("Start All", self.on_click_start), ("Stop All", self.on_click_stop)],
            [("Start Log", self.on_start_logging), ("Stop Log", self.on_stop_logging)],
            [("Auto-Scale", self.auto_scale), ("Reset All", self.reset_plot)],
        ]
        for group in button_groups:
            row_layout = create_button_row(group)
            control_layout.addLayout(row_layout)

        # Signal visibility
        signal_row = QVBoxLayout()
        self.choices = ["Show Resultant Plot", "Show Signal A", "Show Signal B", "Show X-Y Plot"]
        self.signal_check = []
        for text in self.choices:
            cb = QCheckBox(text)
            cb.setChecked(True)
            self.signal_check.append(cb)
            signal_row.addWidget(cb)
        control_layout.addLayout(signal_row)

        container = QWidget()
        container.setLayout(control_layout)
        container.setFixedWidth(240)
        return container

    def setup_worker(self):
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

    def on_click_start(self):
        self.generate_graph_widget.start_all()

    def on_click_stop(self):
        self.generate_graph_widget.stop_all()

    def on_start_logging(self):
        self.generate_graph_widget.start_logging_all()

    def on_stop_logging(self):
        self.generate_graph_widget.stop_logging_all()

    def reset_plot(self):
        self.generate_graph_widget.reset_all()

    def auto_scale(self):
        for graph in self.generate_graph_widget.graphs:
            graph.auto_scale()

    def get_user_input(self):
        userinput1 = self.user_input1.currentText()
        userinput2 = self.user_input2.currentText()
        operation = self.operations.currentText()
        constants = self.constant_input.text().strip()

        if userinput1 == "Select a Signal" or userinput2 == "Select a Signal":
            QMessageBox.critical(self, "Error", "Please select a signal")
            return None, None, None, None

        return userinput1, userinput2, operation, constants

    def on_preview_clicked(self):
        user_input1, user_input2, operation, constants = self.get_user_input()
        if not user_input1:
            return

        if operation in ["A + B", "A - B", "A * B", "A / B"]:
            preview = f"{user_input1} {operation[2]} {user_input2}"
        else:
            preview = operation.replace("A", user_input1).replace("B", user_input2)

        if constants:
            preview += f" | Constants: {constants}"

        self.preview_input.setText(preview)

    def on_calculate_plot(self):
        self.on_click_start()
        time_array = np.linspace(0, 1, self.max_points)
        user_input1, user_input2, operation, constants = self.get_user_input()
        if not user_input1:
            return

        result = compute_expression(time_array, user_input1, user_input2, operation, constants)
        if result:
            self.t_computed, self.y_computed = result
            for graph in self.generate_graph_widget.graphs:
                if hasattr(graph, 'graph_template'):
                    graph.graph_template.plot.plot(self.t_computed, self.y_computed, pen=pg.mkPen('r', width=2))

    def update_plot(self, t, y1, y2):
        pass  # handled inside individual GraphWidgets

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()
