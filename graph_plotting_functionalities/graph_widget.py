from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread

from graph_plotting_functionalities.plotting import Signal_list
from src.data_worker import DataWorker
from graph_plotting_functionalities.Graph_Template import GraphTemplate
class GraphWidget(QWidget):
    def __init__(self, graph_id, mode="operation", signal1="Sin", signal2="Cos", num=1):
        super().__init__()
        self.graph_id = graph_id
        self.mode = mode
        self.signal_name=signal1 #name
        self.signal_func = Signal_list[signal1] #function
        self.dt = 0.05  # ensure this is set

        self.initUI()
        self.setup_worker()

    def initUI(self):
        layout = QVBoxLayout()
        self.graph_template = GraphTemplate(
            title=f"Graph {self.graph_id}",
            xlabel="Time (s)",
            ylabel="Amplitude",
            legend=True
        )
        self.individual_controls = QHBoxLayout()
        self.start_btn = QPushButton('Start')
        self.stop_btn = QPushButton('Stop')
        self.reset_btn = QPushButton('Reset')
        for btn in [self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setFixedWidth(200)
            self.individual_controls.addWidget(btn)
        layout.addWidget(self.graph_template)
        layout.addLayout(self.individual_controls)
        self.setLayout(layout)

    def setup_worker(self):
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt,signal_func=self.signal_func) #passing it to thread
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

    def update_plot(self, t, y1, y2=None):
        self.graph_template.generate_color()
        self.graph_template.add_curve(t, y1, label=self.signal_name, pen_color=self.graph_template.pen_color)
