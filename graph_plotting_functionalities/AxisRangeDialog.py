from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QMessageBox
)


def create_label_input_row(pairs,label_width=90, spacing=10):
    row = QHBoxLayout()
    row.setSpacing(spacing)
    for label, input_line_edit in pairs:
        label = QLabel(label)
        label.setFixedWidth(label_width)
        row.addWidget(label)
        row.addWidget(input_line_edit)
    return row


class AxisRangeDialog(QDialog):
    def __init__(self, x_range_current=(0, 10), y_range_current=(-1, 1), parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Axis Range")
        self.setFixedSize(400, 300)

        main_layout = QVBoxLayout()

        # === X Axis Group ===
        x_box = QGroupBox("X Axis Range")
        x_layout = QVBoxLayout()

        self.input_x_min = QLineEdit()
        self.input_x_min.setPlaceholderText("eg:-500")
        self.input_x_max = QLineEdit()
        self.input_x_max.setPlaceholderText(" eg:500")

        label_input_row=create_label_input_row([
            ("Minimum X", self.input_x_min),("Maximum X", self.input_x_max)
        ])
        x_layout.addLayout(label_input_row)
