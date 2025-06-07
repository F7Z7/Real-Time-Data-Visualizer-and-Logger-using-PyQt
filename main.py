import sys #for accesing system
from PyQt5.QtWidgets import QApplication,QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Data Visualizer")
        self.setGeometry(700,300,400,400)
        pass

def main():
    app =QApplication(sys.argv) #use command line arguments
    window = MainWindow() #instance of class
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()