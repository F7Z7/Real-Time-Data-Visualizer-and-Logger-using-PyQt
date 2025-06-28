import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QCheckBox, QComboBox, QLineEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QThread
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
        # declaring flags
        self.plot_start = False
        self.plot_stop = False
        self.is_reset = False

    def setup_worker(self):
        # initialise worker and thread
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Left panel: controls
        self.control_panel = self.setup_controls()
        main_layout.addWidget(self.control_panel)

        # Right panel: Generate_Graph + static plots
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Dynamic user-defined graphs
        self.generate_graph_widget = Generate_Graph()
        right_layout.addWidget(self.generate_graph_widget)

        # Add the full right layout to main layout
        main_layout.addLayout(right_layout)

    def setup_controls(self):
        control_layout = QVBoxLayout()
        control_layout.setSpacing(5)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setAlignment(Qt.AlignTop)

        user_input_layout = QVBoxLayout()
        user_input_layout.setSpacing(5)

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
        math_layout=QVBoxLayout()
        math_layout.addWidget(QLabel("Math Operation Selection"))
        operation_layout = QHBoxLayout()
        operation_layout.setSpacing(5)
        self.operations=QComboBox()
        self.operations.addItems([
            "Choose an operation", "A + B", "A - B", "A * B", "A / B",
            "sin(A)", "cos(B)", "sin(A) + 2*B"
        ])
        operation_layout.addWidget(self.operations)
        math_layout.addLayout(operation_layout)

        math_layout.addWidget(QLabel("Optional Constants"))
        self.constant_input = QLineEdit()
        self.constant_input.setPlaceholderText("eg:2,1.5")
        math_layout.addWidget(self.constant_input)

        self.preview_btn=QPushButton("Preview the expression")
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        math_layout.addWidget(self.preview_btn)
        math_layout.addWidget(QLabel("Preview"))
        self.preview_input=QLineEdit()
        self.preview_input.setEnabled(False)
        math_layout.addWidget(self.preview_input)
        self.calculate_btn=QPushButton("Calculate and Plot")
        math_layout.addWidget(self.calculate_btn)

        self.calculate_btn.clicked.connect(self.on_calculate_plot)


        control_layout.addLayout(math_layout)


        button_groups = [
            [("Start All", self.on_click_start), ("Stop All", self.on_click_stop)],
            [("Auto-Scale", self.auto_scale), ("Reset All", self.reset_plot)],
        ]

        for group in button_groups:
            row_layout = create_button_row(group)
            control_layout.addLayout(row_layout)




        #zoom layout


        signal_row = QVBoxLayout()
        self.choices = ["Show Resultant Plot","Show Signal A", "Show Signal B", "Show X-Y Plot"]
        self.signal_check = []

        for text in self.choices:
            cb = QCheckBox(text)
            cb.setChecked(True)
            self.signal_check.append(cb)
            signal_row.addWidget(cb)

        self.signal_check[0].stateChanged.connect(self.toggle_visible_resultant)
        self.signal_check[1].stateChanged.connect(self.toggle_visible_signal1)
        self.signal_check[2].stateChanged.connect(self.toggle_visible_signal2)
        self.signal_check[3].stateChanged.connect(self.toggle_visible_xy_plot)

        control_layout.addLayout(signal_row)

        container = QWidget()
        container.setLayout(control_layout)
        container.setFixedWidth(240)
        return container


    def setup_plots(self):
        pg.setConfigOptions(antialias=True)
        self.plot_widget1 = pg.PlotWidget()
        self.plot_widget2 = pg.PlotWidget()
        self.plot_widget3 = pg.PlotWidget()

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setBackground('w')
            plot.setFixedHeight(300)
            plot.showGrid(x=True, y=True)
            plot.setContentsMargins(5, 5, 5, 5)
            plot.setLabel("bottom", "Time", units='sec', **{'color': 'black', "font-size": "10pt"})
            plot.setLabel("left", "Amplitude", **{'color': 'black', "font-size": "10pt"})
            plot.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        self.plot_widget3.setLabel("left", "Signal B", **{'color': 'blue', "font-size": "10pt"})
        self.plot_widget3.setLabel("bottom", "Signal A", **{'color': 'red', "font-size": "10pt"})

        self.result_curve = self.plot_widget1.plot(pen=pg.mkPen('r', width=2), name="Math Result",) #will be updTED AT LAST
        self.signal1_curve = self.plot_widget2.plot(pen=pg.mkPen(color='b', width=2), name="Curve 1")
        self.signal2_curve = self.plot_widget2.plot(pen=pg.mkPen(color='g', width=2), name="Curve 2")
        self.xy_plot = self.plot_widget3.plot(pen=pg.mkPen(color='g', width=2), name="X-Y Plot")

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.addLegend()
            plot.setAntialiasing(True)

    def on_click_start(self):
        if self.plot_start:
            QMessageBox.warning(self,"warning","plot is already running")

        if not self.worker_thread.isRunning():
            signal1 = self.user_input1.currentText()
            signal2 = self.user_input2.currentText()

            if signal1 == "Select a Signal" or signal2 == "Select a Signal":
                QMessageBox.warning(self, "Warning", "Please select both Signal A and Signal B.")
                return

            self.plot_start = True
            self.plot_stop = False
            self.is_reset = False

            if not self.worker_thread.isRunning():
                self.worker_thread.start()

            self.worker.start_signal.emit(signal1, signal2)
    def on_click_stop(self):
        if not self.plot_start:
            return  # Already stopped

        self.plot_stop = True
        self.plot_start = False
        if hasattr(self, "worker") and self.worker:
            self.worker.stop_work()
        if hasattr(self, "worker_thread") and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

    def update_plot(self, t, y1, y2):
        if self.plot_stop or self.is_reset:
            return

        self.x.append(t)
        self.signal1_data.append(y1)
        self.signal2_data.append(y2)

        if len(self.x) > self.max_points:
            self.x.pop(0)
            self.signal1_data.pop(0)
            self.signal2_data.pop(0)

        self.signal1_curve.setData(self.x, self.signal1_data)
        self.signal2_curve.setData(self.x, self.signal2_data)
        self.xy_plot.setData(self.signal1_data, self.signal2_data)

        if self.zoom_combo_box.currentText() not in ["X Axis", "Both"]:
            self.plot_widget1.setXRange(self.t - 10, self.t)
            self.plot_widget2.setXRange(self.t - 10, self.t)

    def reset_plot(self):
        self.plot_stop = True
        self.plot_start = False
        self.is_reset = True

#if thread is reset it should also stop adn delte the thread
        if hasattr(self, "worker") and self.worker:
            self.worker.stop_work()
        if hasattr(self, "worker_thread") and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.x.clear()
        self.signal1_data.clear()
        self.signal2_data.clear()

        self.signal1_curve.clear()
        self.signal2_curve.clear()
        self.xy_plot.clear()

        if hasattr(self,"worker"):
            self.worker.deleteLater()
        if hasattr(self,"worker_thread"):
            self.worker_thread.deleteLater()


        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setXRange(0, 10)
            plot.setYRange(-1, 1)


        #setting a newthread
        self.setup_worker()


        self.is_reset = False #full reset complete

    def auto_scale(self):
        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def toggle_visible_signal1(self, state):
        self.signal1_curve.setVisible(state == Qt.Checked)

    def toggle_visible_signal2(self, state):
        self.signal2_curve.setVisible(state == Qt.Checked)

    def toggle_visible_xy_plot(self, state):
        self.xy_plot.setVisible(state == Qt.Checked)

    def toggle_visible_resultant(self, state):
        self.result_curve.setVisible(state == Qt.Checked)
    def get_user_input(self):
        userinput1 = self.user_input1.currentText()
        userinput2 = self.user_input2.currentText()
        operation = self.operations.currentText()
        constants = self.constant_input.text().strip()
        if userinput1 == "Select a Signal" or userinput2 == "Select a Signal":
            QMessageBox.critical(self, "Error", "Please select a Signal")

        return userinput1,userinput2,operation,constants
    def on_preview_clicked(self):

        user_input1, user_input2, operation, constants = self.get_user_input()

        if operation in ["A + B", "A - B", "A * B", "A / B"]:
            preview = f"{user_input1} {operation[2]} {user_input2}" #operation is A + B like that
        else:
            preview = operation.replace("A", user_input1).replace("B", user_input2)

        if constants:
            preview += f" | Constants: {constants}"

        self.preview_input.setText(preview)

    def on_calculate_plot(self):
        self.on_click_start() #automatically starts the plot
        time_array=np.linspace(0,1,self.max_points) #get some points of time
        user_input1, user_input2, operation, constants = self.get_user_input()

        result=compute_expression(time_array, user_input1, user_input2, operation, constants)
        if result:
            self.t_computed,self.y_computed=result
            if hasattr(self, 'result_curve') and self.result_curve:
                self.result_curve.setData(self.t_computed, self.y_computed)
            else:
                self.result_curve = self.plot_widget1.plot(self.t_computed, self.y_computed, pen=pg.mkPen('r', width=2))


    def on_start_logging(self):
        return 0
    def on_stop_logging(self):
        return 0

    def select_folder(self):
        destination_dir = QFileDialog.getExistingDirectory()
        if destination_dir:
            self.destination.setText(destination_dir)
