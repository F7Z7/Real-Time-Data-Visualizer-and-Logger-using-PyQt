from PyQt5.QtCore import QObject, pyqtSignal
import time

class DataWorker(QObject):
    data_ready = pyqtSignal(object, object, object)  # t_list, y_list, y2_list (optional)

    def __init__(self, dt=0.05, signal_func=None):
        super().__init__()
        self.dt = dt
        self.signal_func = signal_func
        self.running = False
        self.t = 0
        self.t_data = []
        self.y_data = []

    def start_work(self):
        self.running = True
        self.t = 0
        self.t_data = []
        self.y_data = []

        while self.running:
            y1 = self.signal_func(self.t)
            MAX_POINTS = 500 #limit the max poisnt

            self.t_data.append(self.t)
            self.y_data.append(y1)
            if len(self.t_data) > MAX_POINTS:
                self.t_data = self.t_data[-MAX_POINTS:]
                self.y_data = self.y_data[-MAX_POINTS:]

            self.data_ready.emit(self.t_data.copy(), self.y_data.copy(), None)

            self.t += self.dt
            time.sleep(self.dt)

    def stop_work(self):
        self.running = False
