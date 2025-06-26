from PyQt5.QtCore import QObject, pyqtSignal,pyqtSlot
from graph_plotting_functionalities.plotting import Signal_list
import time

class DataWorker(QObject):
    data_ready = pyqtSignal(object, object, object)  # t, y1, y2

    def __init__(self, dt=0.05, signal_func=None):
        super().__init__()
        self.dt = dt
        self.signal_func = signal_func
        self.running = False
        self.t = 0

    def start_work(self):
        import threading
        print("Start work running on:", threading.current_thread().name)
        self.running = True
        self.t = 0
        func = self.Signal_list.get(self.signal_name, lambda t: 0)

        while self.running:
            y1 = func(self.t)
            self.data_ready.emit(self.t, y1, None)
            self.t += self.dt
            time.sleep(self.dt)

    def stop_work(self):
        self.running = False
