# from PyQt5.QtWidgets import QLabel
#
#         user_input_layout = QVBoxLayout()
#         self.user_input1 = QComboBox()
#         self.user_input2 = QComboBox()
#         self.user_input1.addItem("Select a Signal")
#         self.user_input2.addItem("Select a Signal")
#
#
#
#         for label, box in [("Signal A", self.user_input1), ("Signal B", self.user_input2)]:
#             user_input_layout.addWidget(QLabel(label))
#             user_input_layout.addWidget(box)
#
#         control_layout.addLayout(user_input_layout)
#
#         math_layout = QVBoxLayout()
#         math_layout.addWidget(QLabel("Math Operation Selection"))
#         self.operations = QComboBox()
#         self.operations.addItems([
#             "Choose an operation", "A + B", "A - B", "A * B", "A / B",
#             "sin(A)", "cos(B)", "sin(A) + 2*B"
#         ])
#         math_layout.addWidget(self.operations)
#
#         math_layout.addWidget(QLabel("Optional Constants"))
#         self.constant_input = QLineEdit()
#         self.constant_input.setPlaceholderText("eg: 2, 1.5")
#         math_layout.addWidget(self.constant_input)
#
#         self.preview_btn = QPushButton("Preview the expression")
#         self.preview_btn.clicked.connect(self.on_preview_clicked)
#         math_layout.addWidget(self.preview_btn)
#
#         math_layout.addWidget(QLabel("Preview"))
#         self.preview_input = QLineEdit()
#         self.preview_input.setEnabled(False)
#         math_layout.addWidget(self.preview_input)
#
#         self.calculate_btn = QPushButton("Calculate and Plot")
#         self.calculate_btn.clicked.connect(self.on_calculate_plot)
#         math_layout.addWidget(self.calculate_btn)
#
#         control_layout.addLayout(math_layout)