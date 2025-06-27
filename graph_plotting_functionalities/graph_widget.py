import random

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread, Qt

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
        self.graph_template = GraphTemplate(
            title=f"Graph {self.graph_id}",
            xlabel="Time (s)",
            ylabel="Amplitude",
            legend=True,
        )
        pen=pg.mkPen(color=self.pen_color,width=self.pen_width)
        self.curve=self.graph_template.plot.plot([],[],pen=pen,name=self.signal_name)

        self.individual_controls = QHBoxLayout()
        self.start_btn = QPushButton('Start')
        self.stop_btn = QPushButton('Stop')
        self.reset_btn = QPushButton('Reset')
        #connection functionalities
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.reset_btn.clicked.connect(self.on_reset_clicked)

        for btn in [self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setFixedWidth(200)
            self.individual_controls.addWidget(btn)
        layout.addWidget(self.graph_template)
        layout.addLayout(self.individual_controls)
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