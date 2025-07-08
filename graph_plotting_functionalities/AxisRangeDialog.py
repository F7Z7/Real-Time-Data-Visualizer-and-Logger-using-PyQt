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

        # x axis
        x_box = QGroupBox("X Axis Range")
        x_layout = QVBoxLayout()

        self.input_x_min = QLineEdit()
        self.input_x_min.setPlaceholderText("eg:100")
        self.input_x_max = QLineEdit()
        self.input_x_max.setPlaceholderText(" eg:500")

        x_label_input_row=create_label_input_row([
            ("Minimum X", self.input_x_min),("Maximum X", self.input_x_max)
        ])
        x_layout.addLayout(x_label_input_row)

        #y axies group
        y_box = QGroupBox("X Axis Range")
        y_layout = QVBoxLayout()

        self.input_y_min = QLineEdit()
        self.input_y_min.setPlaceholderText("eg:-500")
        self.input_y_max = QLineEdit()
        self.input_y_max.setPlaceholderText(" eg:500")

        y_label_input_row = create_label_input_row([
            ("Minimum Y", self.input_y_min), ("Maximum Y", self.input_y_max)
        ])
        y_layout.addLayout(y_label_input_row)


        #adding final buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.setToolTip("Apply the desired Ranges")
        self.apply_button.clicked.connect(on_apply_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel this dialog")
        self.apply_button.clicked.connect(on_cancel_clicked)
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset to old values")
        self.apply_button.clicked.connect(on_reset_clicked)


        for buttons in [self.apply_button, self.cancel_button, self.reset_button]:
            button_layout.addWidget(buttons)

