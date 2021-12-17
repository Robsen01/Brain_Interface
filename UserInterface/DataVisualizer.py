import sys
from time import sleep
sys.path.append('../../Brain_Interface')
import ArduinoToPiDataTransfer.PiDataReceiver as PDR
import FileSaver.FileSaver as FileSaver

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PySide2.QtWidgets import QGridLayout, QLabel, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QPushButton, QComboBox, QGroupBox, QSizePolicy
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
        self.update_timer = QTimer()
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.update_plot)

        self.threshold_timer = QTimer()
        self.threshold_timer.setInterval(500)
        self.threshold_timer.timeout.connect(self.update_threshold)

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
        startbtn_and_cbx_layout = QGridLayout()

        self.threshold_config_lbl = QLabel("Drücken sie Testen, um eine Threshold zu ermitteln.")
        startbtn_and_cbx_layout.addWidget(self.threshold_config_lbl, 1, 1, 1, 5)

        startbtn_and_cbx_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        # setup group with startbtn and Port-selection-comboBox
        threshold_label = QLabel("Threshold: ")
        
        self.threshold = QLineEdit()
        self.threshold.setText("0")
        
        startbtn_and_cbx_layout.addWidget(threshold_label, 2, 1, 1, 1)
        startbtn_and_cbx_layout.addWidget(self.threshold, 2, 2, 1, 1)

        self.threshold_config_btn = QPushButton('Testen', self)
        self.threshold_config_btn.clicked.connect(self.threshold_button)
        startbtn_and_cbx_layout.addWidget(self.threshold_config_btn, 2, 3, 1, 1)

        self.threshold_discard_btn = QPushButton('Verwerfen', self)
        self.threshold_discard_btn.setEnabled(False)
        self.threshold_discard_btn.clicked.connect(self.threshold_discard_button)
        startbtn_and_cbx_layout.addWidget(self.threshold_discard_btn, 2, 4, 1, 1)

        # fill combo box with items
        self.port_cbx = QComboBox()
        for l in PDR.PiDataReceiver.list_possible_ports():
            s1 = ""
            for s2 in l:
                s1 += s2 + " "
            self.port_cbx.addItem(s1, l[0])

        startbtn_and_cbx_layout.addWidget(self.port_cbx, 2, 5, 1, 1)


        startbtn_and_cbx_group.setLayout(startbtn_and_cbx_layout)
        self.layout.addWidget(startbtn_and_cbx_group)

    '''
    Setup the third Groupbox, which holds the Stopbtn and the Savebtn.
    ''' 
    def setup_stopbtn_group(self) -> None:
        stopbtn_group = QGroupBox()
        stopbtn_layout = QHBoxLayout()
        stopbtn_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        record_button = QPushButton('Aufnehmen', self)
        record_button.clicked.connect(self.record_button)
        stopbtn_layout.addWidget(record_button)
        
        pause_button = QPushButton('Stop', self)
        pause_button.clicked.connect(self.pause_button)
        stopbtn_layout.addWidget(pause_button)

        save_button = QPushButton('Speichern', self)
        save_button.clicked.connect(self.save_button)
        stopbtn_layout.addWidget(save_button)

        stopbtn_group.setLayout(stopbtn_layout)
        self.layout.addWidget(stopbtn_group)

    '''
    Redraws the Plot
    '''
    def update_plot(self) -> None:

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.PDR.x_queue, self.PDR.y_values_envlope, 'r')

        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    '''
    Updates the threshold_config_lbl to show the currently determined Threshold
    '''
    def update_threshold(self) -> None:
        m = max(self.PDR.y_values_envlope)
        erg_str = "Der ermittelte Wert ist: " + str(m) + " "
        if m >= 1000:
            erg_str = erg_str + "(Das ist sehr hoch)"
        self.threshold_config_lbl.setText(erg_str)
        

    '''
    Connects to the Arduino and starts the timer, which updates the plot every x milliseconds .
    (the update interval is defined in __init__).
    '''
    def record_button(self) -> None:
        if(self.connect_to_Arduino(arr_len = 10000)):
            self.PDR.connect_new_data_event(self.file_saver.on_new_data)
            self.PDR.clear_arrays()
            self.update_timer.start()
            self.update_plot()

    '''
    Proposes a Threshold and writes it to the determined Threshold to the Threshold-Textbox
    '''
    def threshold_button(self) -> None:
        if self.threshold_timer.isActive() == False:
            if(self.connect_to_Arduino(send_threshold = False, arr_len = 1000)):
                self.update_timer.start()
                self.threshold_timer.start()
                self.update_plot()
                self.threshold_config_btn.setText("Übernehmen")
                self.threshold_discard_btn.setEnabled(True)
        else:
            self.update_timer.stop()
            self.threshold_timer.stop()
            self.threshold_config_btn.setText("Testen")
            self.threshold_discard_btn.setEnabled(False)
            self.threshold.setText(str(max(self.PDR.y_values_envlope)))
            
    '''
    Stops the Threshold testing, without writing the determined Threshold to the Threshold-Textbox
    '''
    def threshold_discard_button(self) -> None:
        self.update_timer.stop()
        self.threshold_timer.stop()
        self.threshold_config_btn.setText("Testen")
        self.threshold_discard_btn.setEnabled(False)

    '''
    Tries to open the Arduino-connection and returns true, if one was opened.
    arr_len is passed to PiDataReceiver.__init__
    send_threshold = True passes the threshold text to PiDataReceiver.__init__
    '''
    def connect_to_Arduino(self, send_threshold = True, arr_len = 10000) -> bool:
        connect = False
        # open connection to Arduino
        try:
            if hasattr(self, "PDR"):
                self.PDR.before_delete()
                del self.PDR
                # delattr(self, "PDR")
                    
            if send_threshold:
                self.PDR = PDR.PiDataReceiver(port = self.port_cbx.currentData(), threshold = int(self.threshold.text()), arr_len = arr_len)
            else:
                self.PDR = PDR.PiDataReceiver(port = self.port_cbx.currentData(), threshold = 0, arr_len = arr_len)

            # wait for PDR to confirm, that the arduino is on that port
            while self.PDR.thread_running and self.PDR.port_confirmed == False:
                pass

            if self.PDR.thread_running and self.PDR.port_confirmed:
                connect = True
            else:
                if hasattr(self, "PDR"):
                    self.PDR.before_delete()
                    del self.PDR
                connect = False

        except:
            if hasattr(self, "PDR"):
                self.PDR.before_delete()
                del self.PDR
            connect = False
        return connect

    '''
    Stop the graph update timer.
    Also stop to save new data with the file_saver.
    '''
    def pause_button(self) -> None:
        self.update_timer.stop()
        
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
