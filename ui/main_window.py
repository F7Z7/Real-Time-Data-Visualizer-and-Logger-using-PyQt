import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QFrame, QCheckBox,QComboBox,QSplitter
)
from PyQt5.QtCore import Qt,QTimer
import pyqtgraph as pg
from src.plotting import sine_graph,cos_graph
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time-Visualiser")
        self.setMinimumSize(1100, 800)
        self.initUI()
        # self.auto_scroll = True
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        #grpah

        self.plot_widget1=pg.PlotWidget()
        layout.addWidget(self.plot_widget1)
        self.plot_widget1.setBackground('w')
        self.plot_widget1.setFixedHeight(300)
        self.plot_widget1.showGrid(x=True, y=True)

        self.plot_widget2 = pg.PlotWidget()
        layout.addWidget(self.plot_widget2)
        self.plot_widget2.setBackground('w')
        self.plot_widget2.setFixedHeight(300)
        self.plot_widget2.showGrid(x=True, y=True)

        #sine and cos wave
        self.plot_widget1.addLegend()
        self.sine_curve = self.plot_widget1.plot(pen=pg.mkPen(color='r',width=5), name="Sine")
        self.plot_widget2.addLegend()

        self.cos_curve = self.plot_widget2.plot(pen=pg.mkPen(color='b',width=5), name="Cosine")

        #for x,y plotting
        self.plot_widget3 = pg.PlotWidget()
        self.plot_widget3.setBackground('w')
        layout.addWidget(self.plot_widget3)
        self.plot_widget3.setFixedHeight(300)
        self.plot_widget3.showGrid(x=True, y=True)
        self.plot_widget3.addLegend()

        self.x_y_plot=self.plot_widget3.plot(pen=pg.mkPen(color='#ff32cc',width=5), name="X vs Y")


        #buttons:Start-reset-stop
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_zoom_button = QPushButton("Reset Zoom")
        # combo boxes
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setCurrentIndex(2)  # initail selection to both axises
        for btn in [self.start_button, self.stop_button, self.reset_button,self.zoom_in_button,self.zoom_out_button,self.reset_zoom_button]:
            button_layout.addWidget(btn) #adding buttons to this layout
            btn.setFixedSize(100, 30)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignHCenter )
        button_layout.addWidget(QLabel("Zoom Mode"))
        button_layout.addWidget(self.zoom_combo_box)

        layout.addLayout(button_layout) #placing this inside amin window

        #chechk boxes for toggling visibilities
        self.choices=["Show Signal A","Show Signal B","Show X-Y Plot"]
        self.signal_check=[]
        for choices in self.choices:
            check_box=QCheckBox(choices)
            check_box.setChecked(True)
            self.signal_check.append(check_box)
            layout.addWidget(check_box)#adding the check box to the layout

        graphLayout=QSplitter(Qt.Orientation.Vertical)
        for plots in [self.plot_widget1,self.plot_widget2,self.plot_widget3]:
            graphLayout.addWidget(plots)

        graphLayout.setSizes([1, 1, 1])
        layout.addWidget(graphLayout)

        self.plot_widget1.setTitle(" Sine Signal")
        self.plot_widget2.setTitle("Cosine Signal")
        self.plot_widget3.setTitle("XY Plot")

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setContentsMargins(5, 5, 5, 5)

        #giving event handlers

        self.start_button.clicked.connect(self.on_click_start)
        self.stop_button.clicked.connect(self.on_click_stop)
        self.reset_button.clicked.connect(self.reset_plot)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        #for toggling viisbility of signals
        self.signal_check[0].stateChanged.connect(self.toggle_visbile_signA)
        self.signal_check[1].stateChanged.connect(self.toggle_visbile_signB)
        self.signal_check[2].stateChanged.connect(self.toggle_visbile_x_y_plot)

        self.timer=QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.phase = 0
        self.t=0
        self.dt=0.05
        self.x=[]
        self.sine_data=[]
        self.cos_data=[]
        self.max_points=200
        self.xmin=0
        self.xmax=0
        self.center=0

    control_panel = QVBoxLayout()
    control_panel.setSpacing(15)

    def on_click_start(self):
        self.timer.start(50)
    def on_click_stop(self):
        self.timer.stop()
    def reset_plot(self):
        #full reset to 0
        self.timer.stop()
        self.t=0
        self.x.clear()
        self.sine_data.clear()
        self.cos_data.clear()#clearing data
        self.sine_curve.clear()
        self.cos_curve.clear()
        self.plot_widget1.setXRange(0, 10)
        self.plot_widget1.setYRange(-1, 1)#so that the axis reset
        self.plot_widget2.setXRange(0, 10)
        self.plot_widget2.setYRange(-1, 1)


    #new zoom logic
    def apply_zoom(self,zoom_in:bool):
        factor = 0.5 if zoom_in else 2
        mode = self.zoom_combo_box.currentText()
        for plot_widget in [self.plot_widget1, self.plot_widget2]:
            x_range, y_range = plot_widget.viewRange()
            x_center = (x_range[0] + x_range[1]) / 2
            y_center = (y_range[0] + y_range[1]) / 2
            if mode in ["X Axis", "Both"]:
                x_width = (x_range[1] - x_range[0]) * factor
                plot_widget.setXRange(x_center - x_width / 2, x_center + x_width / 2)
            if mode in ["Y Axis", "Both"]:
                y_width = (y_range[1] - y_range[0]) * factor
                plot_widget.setYRange(y_center - y_width / 2, y_center + y_width / 2)

    def zoom_in(self):
        self.apply_zoom(zoom_in=True)

    def zoom_out(self):
        self.apply_zoom(zoom_in=False)

    def reset_zoom(self):
        self.plot_widget1.setXRange(self.t,self.t+10)
        self.plot_widget1.setYRange(-1,1)
        self.plot_widget2.setXRange(self.t,self.t+10)
        self.plot_widget2.setYRange(-1,1)

    def update_plot(self):
        self.t+=self.dt #update time
        self.x.append(self.t)
        self.sine_data.append(sine_graph(self.t))
        self.cos_data.append(cos_graph(self.t))


        if len(self.x) > self.max_points:
            self.x.pop(0)
            self.sine_data.pop(0)
            self.cos_data.pop(0)
        #moving the graph

        self.sine_curve.setData(self.x, self.sine_data) #new data given
        self.cos_curve.setData(self.x, self.cos_data)
        self.x_y_plot.setData(self.sine_data, self.cos_data)
        mode = self.zoom_combo_box.currentText()
        if mode not in ["X Axis", "Both"]:
            self.plot_widget1.setXRange(self.t - 10, self.t)
            self.plot_widget2.setXRange(self.t - 10, self.t)


    def toggle_visbile_signA(self,state):
        if(state==Qt.Checked):
            self.sine_curve.setVisible(True)
        else:
            self.sine_curve.setVisible(False)

    def toggle_visbile_signB(self, state):
        if (state == Qt.Checked):
            self.cos_curve.setVisible(True)
        else:
            self.cos_curve.setVisible(False)

    def toggle_visbile_x_y_plot(self,state):
        if(state==Qt.Checked):
            self.x_y_plot.setVisible(True)

        else:
            self.x_y_plot.setVisible(False)