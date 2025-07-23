from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QMessageBox
)

from graph_plotting_functionalities.Graph_Layout import Generate_Graph


class MathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Signal Math Operations")
        self.setGeometry(300, 300, 300, 300)
        self.result = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Input signal dropdowns
        self.user_input1 = QComboBox()
        self.user_input2 = QComboBox()
        self.user_input1.addItem("Select a Signal")
        self.user_input2.addItem("Select a Signal")

        for graph in self.parent.generate_graph_widget.graphs:
            signal_name = graph.signal_name
            self.user_input1.addItem(signal_name)
            self.user_input2.addItem(signal_name)

        for label, combo in [("Signal A", self.user_input1), ("Signal B", self.user_input2)]:
            layout.addWidget(QLabel(label))
            layout.addWidget(combo)

        # Operation selection
        self.operations = QComboBox()
        self.operations.addItems([
            "Choose an operation", "A + B", "A - B", "A * B", "A / B",
            "sin(A)", "cos(B)", "sin(A) + 2*B"
        ])
        layout.addWidget(QLabel("Math Operation Selection"))
        layout.addWidget(self.operations)

        # Optional constant
        self.constant_input = QLineEdit()
        self.constant_input.setPlaceholderText("Optional constant (e.g., 2, 1.5)")
        layout.addWidget(QLabel("Optional Constants"))
        layout.addWidget(self.constant_input)

        # Preview
        self.preview_input = QLineEdit()
        self.preview_input.setEnabled(False)

        preview_btn = QPushButton("Preview the Expression")
        preview_btn.clicked.connect(self.on_preview_clicked)
        layout.addWidget(preview_btn)
        layout.addWidget(QLabel("Preview"))
        layout.addWidget(self.preview_input)

        # Calculate button
        calculate_btn = QPushButton("Calculate and Plot")
        calculate_btn.clicked.connect(self.on_calculate_clicked)
        layout.addWidget(calculate_btn)

        self.setLayout(layout)

    def get_user_input(self):
        input1 = self.user_input1.currentText()
        input2 = self.user_input2.currentText()
        operation = self.operations.currentText()
        constant = self.constant_input.text().strip()

        if operation == "Choose an operation":
            QMessageBox.critical(self, "Error", "Please choose a math operation")
            return None

        if ("A" in operation and input1 == "Select a Signal") or \
           ("B" in operation and input2 == "Select a Signal"):
            QMessageBox.critical(self, "Error", "Please select required signal(s)")
            return None

        return input1, input2, operation, constant

    def on_preview_clicked(self):
        values = self.get_user_input()
        if not values:
            return

        input1, input2, operation, constant = values
        if operation in ["A + B", "A - B", "A * B", "A / B"]:
            symbol = operation[2]
            expression = f"{input1} {symbol} {input2}"
        else:
            expression = operation.replace("A", input1).replace("B", input2)

        if constant:
            expression += f" | Constant: {constant}"

        self.preview_input.setText(expression)

    def on_calculate_clicked(self):
        values = self.get_user_input()
        if not values:
            return

        input1, input2, operation, constant = values
        if operation in ["A + B", "A - B", "A * B", "A / B"]:
            symbol = operation[2]
            expression = f"{input1} {symbol} {input2}"
        else:
            expression = operation.replace("A", input1).replace("B", input2)

        if constant:
            expression += f" | Const={constant}"

        self.result = {
            "input1": input1,
            "input2": input2,
            "operation": operation,
            "constant": constant,
            "expression": expression
        }
        print("Result:", self.result)
        self.accept()

    def get_result(self):
        return self.result
