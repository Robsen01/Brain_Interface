import sys
sys.path.append('../../Brain_Interface')

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PySide2.QtWidgets import QLabel, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QPushButton, QComboBox, QGroupBox
from PySide2.QtCore import QLine, QTimer
import sys
import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class FileSaveDialog(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(FileSaveDialog, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()

        self.setup_graph_group()

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.show()

    def setup_graph_group(self) -> None:
        graph_group = QGroupBox()
        graph_layout = QVBoxLayout()
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)

        graph_layout.addWidget(toolbar)
        graph_layout.addWidget(self.canvas)

        graph_group.setLayout(graph_layout)
        self.layout.addWidget(graph_group)                

def main():
    app = QApplication(sys.argv)
    w = FileSaveDialog()
    ret = app.exec_()
    sys.exit(ret)
    

if __name__ == '__main__':
    main()
