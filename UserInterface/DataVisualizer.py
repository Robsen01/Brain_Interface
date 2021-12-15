import sys
sys.path.append('../../Brain_Interface')
import ArduinoToPiDataTransfer.PiDataReceiver as PDR
import FileSaver.FileSaver as FileSaver

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PySide2.QtWidgets import QLabel, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QPushButton, QComboBox, QGroupBox, QSizePolicy
from PySide2.QtCore import QTimer
import sys
import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')

# https://matplotlib.org/3.5.0/api/backend_bases_api.html#matplotlib.backend_bases.FigureCanvasBase
'''
Canvas, which draws the Graph that shows the Data.
'''
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

'''
Main Window, which holds the Graph and Controls.
'''
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_plot)

        # add the Layout and fill it with the Group boxes
        self.layout = QVBoxLayout()
        self.setup_graph_group()
        self.setup_startbtn_group()
        self.setup_stopbtn_group()

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.file_saver = FileSaver.FileSaver()

        self.show()

    '''
    Setup the first Groupbox, which holds the Graph and the Graph-controls.
    '''
    def setup_graph_group(self) -> None:
        graph_group = QGroupBox()
        graph_layout = QVBoxLayout()

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)

        graph_layout.addWidget(toolbar)
        graph_layout.addWidget(self.canvas)

        # self.canvas.connect()MatplotlibMouseMotion()
        # self.canvas.mpl_connect('button_press_event', self.onButtonPress)

        graph_group.setLayout(graph_layout)
        self.layout.addWidget(graph_group)

    '''
    Setup the second Groupbox, which holds the Intervalfield, the Startbtn and the Port-Combobox.
    '''
    def setup_startbtn_group(self) -> None:
        startbtn_and_cbx_group = QGroupBox()
        startbtn_and_cbx_layout = QHBoxLayout()
        
        startbtn_and_cbx_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        # setup group with startbtn and Port-selection-comboBox
        thresholdLabel = QLabel("Threshold: ")

        self.threshold = QLineEdit()
        self.threshold.setText("0")
        
        startbtn_and_cbx_layout.addWidget(thresholdLabel)
        startbtn_and_cbx_layout.addWidget(self.threshold)

        start_button = QPushButton('Aufnehmen', self)
        startbtn_and_cbx_layout.addWidget(start_button)

        # fill combo box with items
        self.port_cbx = QComboBox()
        for l in PDR.PiDataReceiver.list_possible_ports():
            s1 = ""
            for s2 in l:
                s1 += s2 + " "
            self.port_cbx.addItem(s1, l[0])

        startbtn_and_cbx_layout.addWidget(self.port_cbx)
        startbtn_and_cbx_group.setLayout(startbtn_and_cbx_layout)
        self.layout.addWidget(startbtn_and_cbx_group)
        start_button.clicked.connect(self.start_button)

    '''
    Setup the third Groupbox, which holds the Stopbtn and the Savebtn.
    ''' 
    def setup_stopbtn_group(self) -> None:
        stopbtn_group = QGroupBox()
        stopbtn_layout = QHBoxLayout()
        stopbtn_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        pause_button = QPushButton('Stop', self)
        stopbtn_layout.addWidget(pause_button)

        save_button = QPushButton('Save', self)
        stopbtn_layout.addWidget(save_button)

        stopbtn_group.setLayout(stopbtn_layout)
        self.layout.addWidget(stopbtn_group)
        pause_button.clicked.connect(self.pause_button)
        save_button.clicked.connect(self.save_button)

    '''
    Redraws the Plot
    '''
    def update_plot(self) -> None:

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.PDR.x_queue, self.PDR.y_values_send_envlope, 'r')

        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    '''
    Connects to the Arduino and starts the timer, which updates the plot every x milliseconds .
    (the update interval is defined in __init__).
    '''
    def start_button(self) -> None:
        connect = False
        # open connection to Arduino
        try:
            if not hasattr(self, "PDR"):
                self.PDR = PDR.PiDataReceiver(self.port_cbx.currentData(), int(self.threshold.text())) #80 is the Threshold (We only need a Textbox in the canvas to set it manually)

            connect = True
        except:
            delattr(self, 'PDR')
            connect = False
        
        if(connect):
            self.PDR.connect_new_data_event(self.file_saver.on_new_data)
            self.timer.start()
            self.update_plot()

    '''
    Stop the graph update timer.
    Also stop to save new data with the file_saver.
    '''
    def pause_button(self) -> None:
        self.timer.stop()
        
        # disconnect FileSaver-listener
        if hasattr(self, "PDR"):
            self.PDR.disconnect_new_data_event(self.file_saver.on_new_data)

    '''
    Shows the Save File Dialoge.
    '''
    def save_button(self) -> None:
        self.pause_button()
        self.file_saver.show_save_dialoge()

'''
Open the Main Window
'''
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    ret = app.exec_()
    sys.exit(ret)
    
# only call main, if this is the main file
if __name__ == '__main__':
    main()
