from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PySide2.QtWidgets import QLineEdit, QMainWindow, QVBoxLayout, QWidget, QApplication, QPushButton
from PySide2.QtCore import QTimer
import sys
import matplotlib
import random
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

#        sc = MplCanvas(self, width=5, height=4, dpi=100)
#        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        sc = self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(sc)

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)
        threshold_field = QLineEdit()
        layout.addWidget(threshold_field)
        start_button = QPushButton('Start', self)
        layout.addWidget(start_button)

        pause_button = QPushButton('Stop', self)
        layout.addWidget(pause_button)


        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        start_button.clicked.connect(self.start_button)
        pause_button.clicked.connect(self.pause_button)
        self.show()

    def update_plot(self):

        # Drop off the first y element, append a new one.
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.xdata, self.ydata, 'r')

        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    def start_button(self):

        self.timer.start()
        n_data = 40
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]

        self.update_plot()
        self.show()

    def pause_button(self):
        self.timer.stop()

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
    

if __name__ == '__main__':
    main()
