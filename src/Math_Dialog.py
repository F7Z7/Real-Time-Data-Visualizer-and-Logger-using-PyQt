# Math_Dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
)

def math_dialogue_box(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Signal Math Operations")
    dialog.setGeometry(300,300,300,300)

    layout = QVBoxLayout()

    # === Signal Selection ===
    user_input1 = QComboBox()
    user_input2 = QComboBox()
    user_input1.addItem("Select a Signal")
    user_input2.addItem("Select a Signal")

    for graph in parent.generate_graph_widget.graphs:
        signal_name = graph.signal_name
        user_input1.addItem(signal_name)
        user_input2.addItem(signal_name)

    for label, combo in [("Signal A", user_input1), ("Signal B", user_input2)]:
        layout.addWidget(QLabel(label))
        layout.addWidget(combo)

    operations = QComboBox()
    operations.addItems([
        "Choose an operation", "A + B", "A - B", "A * B", "A / B",
        "sin(A)", "cos(B)", "sin(A) + 2*B"
    ])
    layout.addWidget(QLabel("Math Operation Selection"))
    layout.addWidget(operations)

    constant_input = QLineEdit()
    constant_input.setPlaceholderText("Optional constant (e.g., 2, 1.5)")
    layout.addWidget(QLabel("Optional Constants"))
    layout.addWidget(constant_input)

    preview_btn = QPushButton("Preview the Expression")
    preview_input = QLineEdit()
    preview_input.setEnabled(False)

    def get_user_input():
        userinput1 = user_input1.currentText()
        userinput2 = user_input2.currentText()
        operation = operations.currentText()
        constants = constant_input.text().strip()

        if operation == "Choose an operation":
            QMessageBox.critical(parent, "Error", "Please choose a math operation")
            return None, None, None, None

        if ("A" in operation and userinput1 == "Select a Signal") or \
                ("B" in operation and userinput2 == "Select a Signal"):
            QMessageBox.critical(dialog, "Error", "Please select required signal(s)")
            return None, None, None, None

        return userinput1, userinput2, operation, constants

    def on_preview_clicked():
        input1,input2,operation,constant=get_user_input()
        if not input1:
            return None
        if operation in ["A + B", "A - B", "A * B", "A / B"]:
            symbol = operation[2]
            preview = f"{input1} {symbol} {input2}"
        else:
            preview = operation.replace("A", user_input1).replace("B", user_input2)

        if constant:
            preview += f" | Constant: {constant}"

        preview_input.setText(preview)

    preview_btn.clicked.connect(on_preview_clicked)

    layout.addWidget(preview_btn)
    layout.addWidget(QLabel("Preview"))
    layout.addWidget(preview_input)

    calculate_btn = QPushButton("Calculate and Plot")
    layout.addWidget(calculate_btn)

    dialog.setLayout(layout)
    dialog.exec_()
