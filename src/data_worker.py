from PyQt5.QtCore import QObject, pyqtSignal
from src.plotting import sine_graph,cos_graph
import time

class DataWorker(QObject):

    data_ready=pyqtSignal([float,float,float]) #t,sine,cos
    def __init__(self, dt=0.05):
        super().__init__()
        self.dt=dt #tim-step
        self.running=False
        self.t=0 #inital time

    def start_work(self):
        self.running=True
        self.t=0
        while self.running:
            sine_val=sine_graph(self.t)
            cos_val=cos_graph(self.t)
            self.data_ready.emit(self.t, sine_val, cos_val) #gives value to the ui
            self.t+=self.dt
            time.sleep(self.dt) #suspends action

    def stop_work(self):
        self.running=False