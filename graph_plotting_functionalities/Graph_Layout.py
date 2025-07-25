# === Graph_Layout.py ===
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from graph_plotting_functionalities.graph_widget import GraphWidget
from graph_plotting_functionalities.plotting import Signal_list
import numpy as np

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
                graph_widget = GraphWidget(graph_id=i + 1, graph_manager=self, signal1=signal_name, num=total_graphs)
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

    def start_logging_all(self, log_format, destination,max_file_size,create_new_file):

        for graph in self.graphs:
            # graph.size_combo.setCurrentText(size)
            graph.start_logging(destination,max_file_size,log_format,create_new_file)

    def stop_logging_all(self):
        for graph in self.graphs:
            graph.stop_logging()

    def get_signal_data_by_name(self, name):
        for graph in self.graphs:
            if graph.signal_name == name:
                if graph.curve is not None:
                    x_data, y_data = graph.curve.getData()
                    return x_data, y_data
                else:
                    print("Warning: No curve data available for", name)
                    return None, None
        print(f"Warning: Signal '{name}' not found in existing graphs.")
        return None, None

    def add_math_plot(self, input1, input2, operation, constant, expression):

        """Create a new graph widget for math operation result"""
        try:
            # Create new math graph widget with unique ID
            new_graph_id = len(self.graphs) + 1

            # Use a valid signal name from Signal_list for initialization
            signal_names = list(Signal_list.keys())
            initial_signal = signal_names[0] if signal_names else "Sin"

            print(f"Creating math graph with ID: {new_graph_id}")


            math_graph = GraphWidget(
                graph_id=new_graph_id,
                graph_manager=self,
                mode="math",  # Set mode to math
                signal1=initial_signal,  # Use valid signal name initially
                num=len(self.graphs) + 1
            )

            # Configure it as math expression
            math_graph.set_as_math_expression(input1, input2, operation, constant)

            # Update the signal name to reflect the expression
            math_graph.signal_name = expression

            # Update the graph title and curve name
            math_graph.graph_template.plot.setTitle(f"Math Result: {expression}")
            math_graph.graph_template.plot.addLegend(f"Math Result: {expression}")

            # Update the curve name in the legend
            if math_graph.curve:
                math_graph.curve.opts['name'] = expression

                legend = math_graph.graph_template.plot.plotItem.legend
                if legend:
                    legend.removeItem(math_graph.curve)  # Remove old entry if exists
                    legend.addItem(math_graph.curve, expression)  # Add with new name

            # Add to graphs list and layout
            self.graphs.append(math_graph)
            self.dynamic_graphs_layout.addWidget(math_graph)


            # Start the math plot after a small delay to ensure everything is set up
            QTimer.singleShot(100, math_graph.start_plot)

        except Exception as e:
            import traceback
            print(f"Error adding math plot: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(None, "Error", f"Failed to add math plot: {str(e)}")

        except Exception as e:
            print(f"Error adding math plot: {e}")
            QMessageBox.critical(None, "Error", f"Failed to add math plot: {str(e)}")



