# Math_Dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
)

def math_dialogue_box(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Signal Math Operations")

    layout = QVBoxLayout()

    # === Signal Selection ===
    user_input1 = QComboBox()
    user_input2 = QComboBox()
    user_input1.addItem("Select a Signal")
    user_input2.addItem("Select a Signal")

    # Populate with available signals
    for graph in parent.generate_graph_widget.graphs:
        signal_name = graph.signal_name
        user_input1.addItem(signal_name)
        user_input2.addItem(signal_name)

    for label, combo in [("Signal A", user_input1), ("Signal B", user_input2)]:
        layout.addWidget(QLabel(label))
        layout.addWidget(combo)

    # === Operation Selection ===
    operations = QComboBox()
    operations.addItems([
        "Choose an operation", "A + B", "A - B", "A * B", "A / B",
        "sin(A)", "cos(B)", "sin(A) + 2*B"
    ])
    layout.addWidget(QLabel("Math Operation Selection"))
    layout.addWidget(operations)

    # === Constant Input ===
    constant_input = QLineEdit()
    constant_input.setPlaceholderText("Optional constant (e.g., 2, 1.5)")
    layout.addWidget(QLabel("Optional Constants"))
    layout.addWidget(constant_input)

    # === Preview Button & Output ===
    preview_btn = QPushButton("Preview the Expression")
    preview_input = QLineEdit()
    preview_input.setEnabled(False)

    def on_preview_clicked():
        # Example: Just show selected operation
        op = operations.currentText()
        preview_input.setText(op)

    preview_btn.clicked.connect(on_preview_clicked)

    layout.addWidget(preview_btn)
    layout.addWidget(QLabel("Preview"))
    layout.addWidget(preview_input)

    # === Calculate Button ===
    calculate_btn = QPushButton("Calculate and Plot")
    layout.addWidget(calculate_btn)

    dialog.setLayout(layout)
    dialog.exec_()
