from PyQt5.QtCore import QObject, pyqtSignal,pyqtSlot
from src.plotting import (
    sine_graph, cos_graph, tan_graph, cot_graph,
    cosec_graph, sec_graph, square_graph, triangle_graph
)
import time

class DataWorker(QObject):
    data_ready = pyqtSignal(float, float, float)  # t, y1, y2
    start_signal=pyqtSignal(str,str)

    def __init__(self, dt=0.05):
        super().__init__()
        self.dt = dt  # time step
        self.running = False
        self.t = 0    # initial time
        self.start_signal.connect(self.start_work)
        self.signal_map = {
            "Sine": sine_graph,
            "Cosine": cos_graph,
            "Tangent": tan_graph,
            "Cosecant": cosec_graph,
            "Secant": sec_graph,
            "Cotangent": cot_graph,
            "Square": square_graph,
            "Triangle": triangle_graph
        }

    @pyqtSlot(str, str)
    def start_work(self, signal1, signal2):
        try:
            import threading
            print("Start work running on:", threading.current_thread().name)
            self.running = True
            self.t = 0

            while self.running:
                func1 = self.signal_map.get(signal1, lambda t: 0)  # find the correspodning signal from map
                func2 = self.signal_map.get(signal2, lambda t: 0)

                y1 = func1(self.t)
                y2 = func2(self.t)

                self.data_ready.emit(self.t, y1, y2)

                self.t += self.dt
                time.sleep(self.dt)
        except Exception as e:
            print("error :",e)

    def stop_work(self):
        self.running = False
