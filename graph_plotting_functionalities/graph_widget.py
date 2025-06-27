import random

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel,QHBoxLayout, QPushButton, QComboBox, QSizePolicy, QGroupBox, QSpacerItem
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QIcon


from graph_plotting_functionalities.plotting import Signal_list
from src.data_worker import DataWorker
from graph_plotting_functionalities.Graph_Template import GraphTemplate
import pyqtgraph as pg
class GraphWidget(QWidget):
    def __init__(self, graph_id, mode="operation", signal1="Sin", signal2="Cos", num=1):
        super().__init__()
        self.graph_id = graph_id
        self.mode = mode
        self.signal_name=signal1 #name
        self.signal_func = Signal_list[signal1] #function
        self.dt = 0.05  # ensure this is set


        self.pen_color = self.generate_color()
        self.pen_width = 3
        self.curve=None

        self.initUI()
        self.setup_worker()

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

        button_layout = QHBoxLayout()
        self.start_btn = QPushButton('Start')
        self.stop_btn = QPushButton('Stop')
        self.reset_btn = QPushButton('Reset')

        for btn in [self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setFixedWidth(120)
            button_layout.addWidget(btn)

        zoom_layout = QHBoxLayout()
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.setFixedWidth(100)
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setToolTip("Choose axis to zoom")

        self.zoom_in_btn = QPushButton('＋ Zoom In')
        self.zoom_out_btn = QPushButton('－ Zoom Out')
        self.auto_scale_btn = QPushButton('Auto-scale')

        for widg in [self.zoom_combo_box, self.zoom_in_btn, self.zoom_out_btn,self.auto_scale_btn]:
            widg.setFixedWidth(100)
            zoom_layout.addWidget(widg)

        # Add to layout
        controls_layout.addLayout(button_layout)
        controls_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        controls_layout.addLayout(zoom_layout)
        controls_box.setLayout(controls_layout)
        layout.addWidget(controls_box)

        # Connections
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.auto_scale_btn.clicked.connect(self.auto_scale)



        # Apply main layout
        layout.addStretch()
        self.setLayout(layout)

    def generate_color(self):
        chars = '0123456789ABCDEF'
        return  "#" + "".join(random.choice(chars) for _ in range(6))
    def setup_worker(self):
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt,signal_func=self.signal_func) #passing it to thread
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

    def clean_up_worker(self):
        if self.worker:
            self.worker.stop_work()
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

    def update_plot(self, t, y1, y2=None):
        self.curve.setData(t,y1)

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

        pen=pg.mkPen(color=self.pen_color,width=self.pen_width)
        self.curve = self.graph_template.plot.plot([], [], pen=pen, name=self.signal_name)

        self.setup_worker()

    def apply_zoom(self, zoom_in: bool):
        factor = 0.5 if zoom_in else 2
        mode = self.zoom_combo_box.currentText()

        plot_widget=self.graph_template.plot
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
        plot_widget=self.graph_template.plot
        plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)