import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QFrame, QCheckBox,QComboBox,QSplitter
)
from PyQt5.QtCore import Qt,QTimer,QThread
import pyqtgraph as pg
from src.data_worker import DataWorker
from src.plotting import sine_graph,cos_graph
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time-Visualiser")
        self.setMinimumSize(1100, 800)
        self.initUI()
        # self.auto_scroll = True
        self.worker_thread = QThread() #create a thread
        self.worker=DataWorker(dt=self.dt)#initate a worker
        self.worker.moveToThread(self.worker_thread)#moving it to parent thread
        self.worker.data_ready.connect(self.update_plot)
        self.worker_thread.started.connect(self.worker.start_work)

        self.destroyed.connect(self.clean_up_worker)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

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


        #buttons:Start-reset-stop-checkboxes
        button_layout = QVBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.auto_scale_button = QPushButton("Auto-Scale")
        # combo boxes
        self.zoom_combo_box = QComboBox()
        self.zoom_combo_box.addItems(["X Axis", "Y Axis", "Both"])
        self.zoom_combo_box.setCurrentIndex(2)  # initail selection to both axises
        for btn in [self.start_button, self.stop_button, self.reset_button,self.zoom_in_button,self.zoom_out_button,self.auto_scale_button]:
            button_layout.addWidget(btn) #adding buttons to this layout
            btn.setFixedSize(100, 30)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignVCenter )
        button_layout.addWidget(QLabel("Zoom Mode"))
        button_layout.addWidget(self.zoom_combo_box)




        #chechk boxes for toggling visibilities
        self.choices=["Show Signal A","Show Signal B","Show X-Y Plot"]
        self.signal_check=[]
        for choices in self.choices:
            check_box=QCheckBox(choices)
            check_box.setChecked(True)
            self.signal_check.append(check_box)
            button_layout.addWidget(check_box)#adding the check box to the layout

        button_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(12)

        control_widget = QWidget()
        control_widget.setLayout(button_layout)
        control_widget.setFixedWidth(160)

        layout.addWidget(control_widget)
        graphLayout=QSplitter(Qt.Orientation.Vertical)
        for plots in [self.plot_widget1,self.plot_widget2,self.plot_widget3]:
            graphLayout.addWidget(plots)

        graphLayout.setSizes([1, 1, 1])
        layout.addWidget(graphLayout)

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setContentsMargins(5, 5, 5, 5)
            plot.setLabel("bottom", "Time",units ='sec',**{'color':'black',"font-size":"10pt"}) #pt instead of px
            plot.setLabel("left", "Amplitude",**{'color':'black',"font-size":"10pt"})
            plot.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        self.plot_widget3.setLabel("left", "Cos(t)",**{'color':'blue',"font-size":"10pt"})
        self.plot_widget3.setLabel("bottom", "Sin(t)",**{'color':'red',"font-size":"10pt"})


        #giving event handlers

        self.start_button.clicked.connect(self.on_click_start)
        self.stop_button.clicked.connect(self.on_click_stop)
        self.reset_button.clicked.connect(self.reset_plot)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.auto_scale_button.clicked.connect(self.auto_scale)

        #for toggling viisbility of signals

        self.signal_check[0].stateChanged.connect(self.toggle_visbile_signA)
        self.signal_check[1].stateChanged.connect(self.toggle_visbile_signB)
        self.signal_check[2].stateChanged.connect(self.toggle_visbile_x_y_plot)


#timer connections
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


#functionalities
    def on_click_start(self):
        if not self.worker_thread.isRunning(): #check if its already running
            self.worker_thread.start()

    def on_click_stop(self):
        self.worker.stop_work()
        self.worker_thread.quit()
        self.worker_thread.wait()
    def reset_plot(self):
        #full reset to 0
        self.timer.stop()
        self.t=0
        # self.x.clear()
        # self.sine_data.clear()
        # self.cos_data.clear()#clearing data
        # self.sine_curve.clear()
        # self.cos_curve.clear()
        for curve_data in [self.sine_data,self.cos_data,self.sine_curve,self.cos_curve,self.x,self.x_y_plot]:
            curve_data.clear()

        for plot in [self.plot_widget1, self.plot_widget2, self.plot_widget3]:
            plot.setXRange(0,10)
            plot.setYRange(-1,1)

    #new zoom logic
    def apply_zoom(self,zoom_in:bool):
        factor = 0.5 if zoom_in else 2
        mode = self.zoom_combo_box.currentText()
        for plot_widget in [self.plot_widget1, self.plot_widget2,self.plot_widget3]:
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

    def auto_scale(self):
        # self.plot_widget1.setXRange(self.t,self.t+10)
        # self.plot_widget1.setYRange(-1,1)
        # self.plot_widget2.setXRange(self.t,self.t+10)
        # self.plot_widget2.setYRange(-1,1)
        for plot in [self.plot_widget1, self.plot_widget2,self.plot_widget3]:
            plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)


    def update_plot(self,t,sin,cos):
        self.t #update time
        self.x.append(t)
        self.sine_data.append(sin)
        self.cos_data.append(cos)


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

    def clean_up_worker(self):
        if self.worker_thread.isRunning():
            self.worker.stop_work()
            self.worker_thread.quit()
            self.worker_thread.wait()

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