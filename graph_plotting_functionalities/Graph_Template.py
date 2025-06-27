import random
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class GraphTemplate(QWidget):
    def __init__(self, title="Signal Plot", xlabel="Time (s)", ylabel="Amplitude", legend=False, height=300):
        super().__init__()
        self.setFixedHeight(height)

        self.plot = pg.PlotWidget()
        self.plot.setAntialiasing(True)
        self.initUI(title, xlabel, ylabel, legend, height)

    def initUI(self, title, xlabel, ylabel, legend, height):
        self.plot.setTitle(title)
        self.plot.setBackground("w")
        self.plot.showGrid(x=True, y=True)
        self.plot.setContentsMargins(5, 5, 5, 5)

        self.plot.setLabel("bottom", xlabel, **{'color': 'black', "font-size": "10pt"})
        self.plot.setLabel("left", ylabel, **{'color': 'black', "font-size": "10pt"})
        self.plot.setTitle(title, **{'color': 'black', "size": "12pt"})

        self.plot.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        if legend:
            self.plot.addLegend()

        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)

    def add_curve(self, x_data, y_data, label="Signal", pen_color="r", width=5):
        pen = pg.mkPen(color=pen_color, width=width)
        return self.plot.plot(x_data, y_data, pen=pen, name=label)