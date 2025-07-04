# === Graph_Layout.py ===
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from graph_plotting_functionalities.graph_widget import GraphWidget
from graph_plotting_functionalities.plotting import Signal_list


class Generate_Graph(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 800)
        self.graphs = []
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.dynamic_graphs_layout = QVBoxLayout(self.scroll_content)
        self.dynamic_graphs_layout.setSpacing(0)
        self.scroll_area.setWidget(self.scroll_content)

        self.initUI()

    def initUI(self):
        graph_layout = QVBoxLayout()
        graph_layout.setSpacing(5)

        # === Graph Count Input Panel ===
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(QLabel('Set the number of graphs'))
        sub_layout.setAlignment(Qt.AlignTop)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel('Enter no of graphs'))
        self.inupt_graphs = QLineEdit()
        self.inupt_graphs.setPlaceholderText("e.g. 3")
        input_layout.addWidget(self.inupt_graphs)

        sub_layout.addLayout(input_layout)

        self.set_btn = QPushButton('Set')
        self.set_btn.clicked.connect(self.on_set_clicked)
        sub_layout.addWidget(self.set_btn)

        graph_layout.addLayout(sub_layout)
        graph_layout.addLayout(self.dynamic_graphs_layout)
        graph_layout.addWidget(self.scroll_area)
        self.setLayout(graph_layout)

    def on_set_clicked(self):
        try:
            total_graphs = int(self.inupt_graphs.text())
            if total_graphs <= 0:
                QMessageBox.warning(self, "Error", "Please enter a positive number")
                return

            # Clear old widgets
            for i in reversed(range(self.dynamic_graphs_layout.count())):
                widget = self.dynamic_graphs_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            self.graphs = []
            signal_names = list(Signal_list.keys())

            for i in range(total_graphs):
                signal_name = signal_names[i % len(signal_names)]
                graph_widget = GraphWidget(graph_id=i + 1, signal1=signal_name, num=total_graphs)
                self.graphs.append(graph_widget)
                self.dynamic_graphs_layout.addWidget(graph_widget)

        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid Value")

    # === Global Control Methods ===

    def start_all(self):
        for graph in self.graphs:
            graph.start_plot()

    def stop_all(self):
        for graph in self.graphs:
            graph.stop_plot()

    def reset_all(self):
        for graph in self.graphs:
            graph.reset_plot()

    def start_logging_all(self, log_format, destination):

        for graph in self.graphs:
            # graph.size_combo.setCurrentText(size)
            graph.start_logging(destination,log_format)

    def stop_logging_all(self):
        for graph in self.graphs:
            graph.stop_logging()
