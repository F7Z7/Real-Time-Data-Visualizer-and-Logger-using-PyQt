import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import pyqtgraph as pg
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        self.plot_widget = pg.PlotWidget()
        self.graphPlotter.layout().addWidget(self.plot_widget)

        self.startPlot.clicked.connect(self.plot_rand)
        self.resetPlot.clicked.connect(self.plot_reset)
    def plot_rand(self):

        fromVal=int(self.fromInput.toPlainText())
        toVal=int(self.toInput.toPlainText())

        x=list(range(fromVal,toVal))
        y=[random.uniform(0,100) for _ in x]

        self.plot_widget.clear()
        self.plot_widget.plot(x, y, pen=None, symbol='o', symbolSize=7, symbolBrush='b')
        self.plot_widget.setLabel('bottom', 'x axis')
        self.plot_widget.setLabel('left', 'random value')
        self.plot_widget.setXRange(fromVal, toVal)
        self.plot_widget.setYRange(0, 100)


    def plot_reset(self):
        self.plot_widget.clear()
        self.fromInput.clear()
        self.toInput.clear()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
