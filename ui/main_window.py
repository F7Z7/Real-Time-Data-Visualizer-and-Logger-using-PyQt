# === main_window.py ===
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QComboBox, QLineEdit, QMessageBox, QFileDialog, QCheckBox, QDialog
)
from PyQt5.QtCore import Qt, QThread, QEvent
import numpy as np
import pyqtgraph as pg
from src.Math_Dialog import MathDialog
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

        # first this is intialised
        self.generate_graph_widget = Generate_Graph()
        self.generate_graph_widget.graphs_updated = self.update_visibility_checkboxes

        self.control_panel = self.setup_controls()
        main_layout.addWidget(self.control_panel)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        right_layout.addWidget(self.generate_graph_widget)

        main_layout.addLayout(right_layout)

    def setup_controls(self):
        control_layout = QVBoxLayout()
        control_layout.setSpacing(5)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setAlignment(Qt.AlignTop)

        # math operation dialogue box entry
        self.math_controls = QPushButton("Signal Operations")
        self.math_controls.setToolTip("Click to do signal manipulations")
        self.math_controls.clicked.connect(self.open_math_dialog)

        control_layout.addWidget(self.math_controls)

        # Global Buttons
        control_layout.addWidget(QLabel("Playback Controls"))
        button_groups = [
            [("Start All", self.on_click_start), ("Stop All", self.on_click_stop)],
            [("Auto-Scale", self.auto_scale), ("Reset All", self.reset_plot)],
        ]
        for group in button_groups:
            row_layout = create_button_row(group)
            control_layout.addLayout(row_layout)
        zoom_layout = QVBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom Axis:"))
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        zoom_layout.addWidget(self.zoom_combo_box)

        zoom_btn_layout = create_button_row([
            ("＋ Zoom In", self.zoom_in),
            ("－ Zoom Out", self.zoom_out)
        ])
        zoom_layout.addLayout(zoom_btn_layout)
        control_layout.addLayout(zoom_layout)

        # File Format
        control_layout.addWidget(QLabel("File Format:"))
        self.logger_combo_box = QComboBox()
        self.logger_combo_box.addItems(["Select format", "CSV", "Binary"])
        control_layout.addWidget(self.logger_combo_box)

        # File Size
        control_layout.addWidget(QLabel("Max Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1MB", "5MB", "10MB", "50MB", "100MB"])
        control_layout.addWidget(self.size_combo)
        self.new_file = QComboBox()
        self.new_file.addItems(["Stop when file size exceed the limit", "Create a new file after limit is exceeded"])
        control_layout.addWidget(self.new_file)

        # Destination selection
        control_layout.addWidget(QLabel("Select Destination:"))
        self.destination = QLineEdit()
        self.destination.setPlaceholderText("Click to select folder...")
        self.destination.setReadOnly(True)
        self.destination.setCursor(Qt.PointingHandCursor)
        self.destination.mousePressEvent = lambda e: self.select_folder()
        control_layout.addWidget(self.destination)

        # Start/Stop Logging
        self.start_log_btn = QPushButton("Start Log")
        self.stop_log_btn = QPushButton("Stop Log")

        # Initially disable "Stop Log"
        self.stop_log_btn.setEnabled(False)

        # Connect signals
        self.start_log_btn.clicked.connect(self.on_start_logging)
        self.stop_log_btn.clicked.connect(self.on_stop_logging)

        log_btns = create_button_row([
            ("Start Log", self.start_log_btn.click),
            ("Stop Log", self.stop_log_btn.click)
        ])

        control_layout.addLayout(log_btns)

        # Signal visibility
        self.visibility_layout = QVBoxLayout()
        self.visibility_layout.addWidget(QLabel("Graph Visibility:"))

        self.master_checkbox = QCheckBox("Show All Graphs")
        self.master_checkbox.setChecked(True)
        self.master_checkbox.stateChanged.connect(self.toggle_all_graphs)
        self.master_checkbox.setToolTip("For Master Visibility Control")
        self.visibility_layout.addWidget(self.master_checkbox)
        # will be added dynamically
        self.check_box_layout = QVBoxLayout()
        self.visibility_layout.addLayout(self.check_box_layout)

        control_layout.addLayout(self.visibility_layout)

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
        self.stop_log_btn.setEnabled(True)
        self.start_log_btn.setEnabled(False)
        destination = self.destination.text()
        log_format = self.logger_combo_box.currentText()
        size = self.size_combo.currentText()
        if self.new_file.currentText() == "Stop when file size exceed the limit":
            create_new_file = True
        else:
            create_new_file = False
        if log_format == "Select format":
            QMessageBox.warning(self, "Warning", "Please select a valid file format.")
            return
        if not destination:
            QMessageBox.warning(self, "Warning", "Please select a destination folder.")
            return

        size_map = {
            "1MB": 1 * 1024 * 1024,
            "5MB": 5 * 1024 * 1024,
            "10MB": 10 * 1024 * 1024,
            "50MB": 50 * 1024 * 1024,
            "100MB": 100 * 1024 * 1024,
        }
        max_size = size_map.get(size, 1 * 1024 * 1024)  # default is 1mb
        self.generate_graph_widget.start_logging_all(log_format, destination, max_size, create_new_file)

    def on_stop_logging(self):
        self.start_log_btn.setEnabled(True)
        self.stop_log_btn.setEnabled(False)
        self.generate_graph_widget.stop_logging_all()

    def reset_plot(self):
        self.generate_graph_widget.reset_all()

    def auto_scale(self):
        for graph in self.generate_graph_widget.graphs:
            graph.auto_scale()

    # def get_user_input(self):
    #     userinput1 = self.user_input1.currentText()
    #     userinput2 = self.user_input2.currentText()
    #     operation = self.operations.currentText()
    #     constants = self.constant_input.text().strip()
    #
    #     if userinput1 == "Select a Signal" or userinput2 == "Select a Signal":
    #         QMessageBox.critical(self, "Error", "Please select a signal")
    #         return None, None, None, None
    #
    #     return userinput1, userinput2, operation, constants
    #
    # def on_preview_clicked(self):
    #     user_input1, user_input2, operation, constants = self.get_user_input()
    #     if not user_input1:
    #         return
    #
    #     if operation in ["A + B", "A - B", "A * B", "A / B"]:
    #         preview = f"{user_input1} {operation[2]} {user_input2}"
    #     else:
    #         preview = operation.replace("A", user_input1).replace("B", user_input2)
    #
    #     if constants:
    #         preview += f" | Constants: {constants}"
    #
    #     self.preview_input.setText(preview)
    #
    # def on_calculate_plot(self):
    #     self.on_click_start()
    #     time_array = np.linspace(0, 1, self.max_points)
    #     user_input1, user_input2, operation, constants = self.get_user_input()
    #     if not user_input1:
    #         return
    #
    #     result = compute_expression(time_array, user_input1, user_input2, operation, constants)
    #     if result:
    #         self.t_computed, self.y_computed = result
    #         for graph in self.generate_graph_widget.graphs:
    #             if hasattr(graph, 'graph_template'):
    #                 graph.graph_template.plot.plot(self.t_computed, self.y_computed, pen=pg.mkPen('r', width=2))

    def update_plot(self, t, y1, y2):
        pass  # handled inside individual GraphWidgets

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

    def eventFilter(self, obj, event):
        if obj == self.destination and event.type() == QEvent.MouseButtonPress:
            self.select_folder()
            return True
        return super().eventFilter(obj, event)

    def select_folder(self):
        # stop the plot
        self.generate_graph_widget.stop_all()

        folder = QFileDialog.getExistingDirectory()

        # resume after selction
        self.generate_graph_widget.start_all()
        if folder:
            self.destination.setText(folder)
            self.destination.setToolTip(f"Selected: {folder}")

    def zoom_in(self):
        zoom_mode = self.zoom_combo_box.currentText()
        for graph in self.generate_graph_widget.graphs:
            graph.zoom_in_all(zoom_mode)

    def zoom_out(self):
        zoom_mode = self.zoom_combo_box.currentText()
        for graph in self.generate_graph_widget.graphs:
            graph.zoom_out_all(zoom_mode)

    # this is for adding  the current signals to the combobox
    def add_dynamic_signals(self):
        self.user_input1.clear()
        self.user_input2.clear()

        self.user_input1.addItem("Select a Signal")
        self.user_input2.addItem("Select a Signal")

        signal_names = []
        for graph in self.generate_graph_widget.graphs:
            signal_names.append(graph.name)

        for name in sorted(set(signal_names)):
            self.user_input1.addItem(name)
            self.user_input2.addItem(name)

    def open_math_dialog(self):
        dialog = MathDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_result()
            if result:
                self.generate_graph_widget.add_math_plot(
                    input1=result["input1"],
                    input2=result["input2"],
                    operation=result["operation"],
                    constant=result["constant"],
                    expression=result["expression"]
                )

    def update_visibility_checkboxes(self):

        for i in reversed(range(self.check_box_layout.count())):
            widget = self.check_box_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.signal_check = []
        self.check_box_layout.addWidget(QLabel("Individual Signal Visibility check"))

        for i, graph in enumerate(self.generate_graph_widget.graphs):
            check_box = QCheckBox(f"{graph.graph_id} : {graph.signal_name}")
            check_box.setChecked(True)
            check_box.stateChanged.connect(lambda state, idx=i: self.toggle_single_graph(idx, state))
            self.signal_check.append(check_box)
            self.check_box_layout.addWidget(check_box)

    def toggle_all_graphs(self, state):
        visible = (state == Qt.Checked)
        for graph in self.generate_graph_widget.graphs:
            # Show/hide the graph widget

            graph.setVisible(visible)
        for checkbox in self.signal_check:
            checkbox.setChecked(visible)

    def toggle_single_graph(self, idx, state, graph=None):
        visible = (state == Qt.Checked)
        self.generate_graph_widget.graphs[idx].setVisible(visible)
