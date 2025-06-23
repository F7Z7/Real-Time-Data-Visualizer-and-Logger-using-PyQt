import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QFrame, QCheckBox, QComboBox, QSplitter,
    QLineEdit, QSpacerItem, QSizePolicy, QMessageBox,QFileDialog,QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QThread
import pyqtgraph as pg
from pyqtgraph.examples.CustomGraphItem import Graph

from src.data_worker import DataWorker


class GraphWidget(QWidget):
    def __init__(self,graph_id,mode="operation", signal1="Sin", signal2="Cos",num=1):
        super().__init__()
        self.graph_id = graph_id
        self.mode = mode
        self.signals=[]
        self.signals = [f"{signal1}_{i}" for i in range(num)]

        self.initUI()
        self.setup_worker()
    def setup_worker(self):
        self.worker_thread = QThread()
        self.worker = DataWorker(dt=self.dt)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.update_plot)
        self.destroyed.connect(self.clean_up_worker)

class Generate_Graph(QWidget):
    def __init__(self, graph_id=None):
        super().__init__()
        self.setMinimumSize(1000, 800)
        self.graphs = []
        self.dynamic_graphs_layout = QVBoxLayout()
        self.initUI()


    def initUI(self):
        graphLayout = QVBoxLayout()
        graphLayout.setAlignment(Qt.AlignTop)
        graphLayout.setSpacing(5)

        # Input section to choose number of graphs
        input_graph_layout = QHBoxLayout()
        input_graph_layout.addWidget(QLabel("Enter no of graphs"))

        self.input_text = QLineEdit()
        input_graph_layout.addWidget(self.input_text)

        self.input_btn = QPushButton("Set")
        input_graph_layout.addWidget(self.input_btn)

        self.input_btn.clicked.connect(self.on_set_clicked)

        graphLayout.addLayout(input_graph_layout)

        # Layout to hold dynamically created graph widgets
        graphLayout.addLayout(self.dynamic_graphs_layout)

        # Final layout set
        self.setLayout(graphLayout)
    def on_set_clicked(self):
        try:
            num=int(self.input_text.text())
            if num<=0:
                QMessageBox.warning(self,"Error","Please enter a positive integer")
            self.graph=Generate_Graph()

            #reset old plots
            for i in reversed(range(self.dynamic_graphs_layout.count())):
                widget = self.dynamic_graphs_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            self.graphs = []

            # Add new graph widgets dynamically
            for i in range(num):
                graph_widget = GraphWidget(graph_id=i, num=num)
                self.graphs.append(graph_widget)
                self.dynamic_graphs_layout.addWidget(graph_widget)

        except ValueError:
            QMessageBox.critical(self,"Error","Please enter a  integer")
