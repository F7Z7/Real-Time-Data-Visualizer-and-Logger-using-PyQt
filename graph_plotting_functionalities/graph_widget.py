from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QThread
from src.data_worker import DataWorker
from graph_plotting_functionalities.Graph_Template import GraphTemplate
class GraphWidget(QWidget):
    def __init__(self, graph_id, mode="operation", signal1="Sin", signal2="Cos", num=1):
        super().__init__()
        self.graph_id = graph_id
        self.mode = mode
        self.signals = [f"{signal1}_{i}" for i in range(num)]
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
        layout.addWidget(self.graph_template)
        self.setLayout(layout)

    def setup_worker(self):
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

    def update_plot(self, t, y1, y2):
        # Example data graph_plotting_functionalities
        self.graph_template.add_curve(t, y1, label="Signal A")
        self.graph_template.add_curve(t, y2, label="Signal B")
