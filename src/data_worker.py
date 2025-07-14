from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import time

class DataWorker(QObject):
    data_ready = pyqtSignal(object, object, object)  # t_list, y_list, y2_list (optional)
    MAX_POINTS = 500  # limit the max poisnt

    def __init__(self, dt=0.05, signal_func=None):
        super().__init__()
        self.dt = dt
        self.signal_func = signal_func
        self.running = False
        self.t = 0
        self.t_data = []
        self.y_data = []

    @pyqtSlot()
    def start_work(self):
        self.running = True
        # self.t = 0
        # self.t_data = []
        # self.y_data = []

        while self.running:
            if not hasattr(self, 'data_ready'):
                break  # Avoid using deleted object

            y1 = self.signal_func(self.t)

            self.t_data.append(self.t)
            self.y_data.append(y1)
            if len(self.t_data) >self.MAX_POINTS:
                self.t_data = self.t_data[-self.MAX_POINTS:]
                self.y_data = self.y_data[-self.MAX_POINTS:]
            try:
                self.data_ready.emit(self.t_data.copy(), self.y_data.copy(), None)
            except RuntimeError:
                break
            self.t += self.dt
            time.sleep(self.dt)

    def stop_work(self):
        self.running = False
