from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QMessageBox
)


def create_label_input_row(pairs, label_width=90, spacing=5):
    row = QHBoxLayout()
    row.setSpacing(spacing)
    for label_text, input_line_edit in pairs:
        label = QLabel(label_text)
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
        self.input_x_min = QLineEdit()
        self.input_x_min.setPlaceholderText("e.g. 100")
        self.input_x_max = QLineEdit()
        self.input_x_max.setPlaceholderText("e.g. 500")
        x_label_input_row = create_label_input_row([
            ("Minimum X", self.input_x_min),
            ("Maximum X", self.input_x_max)
        ])
        x_layout = QVBoxLayout()
        x_layout.addLayout(x_label_input_row)
        x_box = QGroupBox("X Axis Range")
        x_box.setLayout(x_layout)
        main_layout.addWidget(x_box)

        # === Y Axis Group ===
        self.input_y_min = QLineEdit()
        self.input_y_min.setPlaceholderText("e.g. -500")
        self.input_y_max = QLineEdit()
        self.input_y_max.setPlaceholderText("e.g. 500")
        y_label_input_row = create_label_input_row([
            ("Minimum Y", self.input_y_min),
            ("Maximum Y", self.input_y_max)
        ])
        y_layout = QVBoxLayout()
        y_layout.addLayout(y_label_input_row)
        y_box = QGroupBox("Y Axis Range")
        y_box.setLayout(y_layout)
        main_layout.addWidget(y_box)

        # === Buttons ===
        self.apply_button = QPushButton("Apply")
        self.apply_button.setToolTip("Apply the desired Ranges")
        self.apply_button.clicked.connect(self.on_apply_clicked)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel this dialog")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset to old values")
        self.reset_button.clicked.connect(self.on_reset_clicked)

        button_layout = QHBoxLayout()
        for btn in [self.apply_button, self.cancel_button, self.reset_button]:
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def on_apply_clicked(self):
        try:
            x_min = float(self.input_x_min.text())
            x_max = float(self.input_x_max.text())
            y_min = float(self.input_y_min.text())
            y_max = float(self.input_y_max.text())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid numeric values.")
            return

        if x_min > x_max or y_min > y_max:
            QMessageBox.warning(self, "Warning", "Minimum must be less than Maximum for both axes.")
            return

        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self.accept()

    def on_cancel_clicked(self):
        self.reject()

    def on_reset_clicked(self):
        self.input_x_min.clear()
        self.input_x_max.clear()
        self.input_y_min.clear()
        self.input_y_max.clear()

    def get_ranges(self):
        return self._x_min, self._x_max, self._y_min, self._y_max
