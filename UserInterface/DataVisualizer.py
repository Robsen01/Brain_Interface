import sys


sys.path.append('../../Brain_Interface')
import ArduinoToPiDataTransfer.PiDataReceiver as PDR
from FileExport import FileOpener, FileSaver

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PySide2.QtWidgets import QGridLayout, QLabel, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QPushButton, QComboBox, QGroupBox, QSizePolicy, QFileDialog, QMessageBox
from PySide2.QtCore import SIGNAL, QTimer, QThread, Signal
import sys
import matplotlib

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
        self.setup_config_group()
        self.setup_controll_group()

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.file_saver = FileSaver.FileSaver()
        self.fileopener = []

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
    Setup the second Groupbox, which holds the threshold-field, the thrshold-config-buttons and the Port-Combobox.
    '''
    def setup_config_group(self) -> None:
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

        self.btn_threshold_config = QPushButton('Testen', self)
        self.btn_threshold_config.clicked.connect(self.on_threshold_button)
        startbtn_and_cbx_layout.addWidget(self.btn_threshold_config, 2, 3, 1, 1)

        self.btn_threshold_discard = QPushButton('Verwerfen', self)
        self.btn_threshold_discard.setEnabled(False)
        self.btn_threshold_discard.clicked.connect(self.on_threshold_discard_button)
        startbtn_and_cbx_layout.addWidget(self.btn_threshold_discard, 2, 4, 1, 1)

        # fill combo box with items
        self.cbx_port = QComboBox()
        for l in PDR.PiDataReceiver.list_possible_ports():
            s1 = ""
            for s2 in l:
                s1 += s2 + " "
            self.cbx_port.addItem(s1, l[0])

        startbtn_and_cbx_layout.addWidget(self.cbx_port, 2, 5, 1, 1)


        startbtn_and_cbx_group.setLayout(startbtn_and_cbx_layout)
        self.layout.addWidget(startbtn_and_cbx_group)

    '''
    Setup the third Groupbox, which holds the Record-button, Stop-button, Save-button and Open-button.
    ''' 
    def setup_controll_group(self) -> None:
        stopbtn_group = QGroupBox()
        stopbtn_layout = QHBoxLayout()
        stopbtn_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        self.btn_record = QPushButton('neue Aufnahme', self)
        self.btn_record.clicked.connect(self.on_record_button)
        stopbtn_layout.addWidget(self.btn_record)
        
        self.btn_pause = QPushButton('Stop', self)
        self.btn_pause.clicked.connect(self.on_pause_button)
        stopbtn_layout.addWidget(self.btn_pause)

        self.btn_open = QPushButton('Speichern', self)
        self.btn_open.clicked.connect(self.on_save_button)
        stopbtn_layout.addWidget(self.btn_open)

        self.btn_open = QPushButton('Öffnen', self)
        self.btn_open.clicked.connect(self.on_open_button)
        stopbtn_layout.addWidget(self.btn_open)

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
    Enables or disables the UI, which interacts with the Arduino-connection
    '''
    def enable_PDR_UI(self, enable = True, enable_btn_threshold_discard = False):
        self.cbx_port.setEnabled(enable)
        self.btn_threshold_discard.setEnabled(enable_btn_threshold_discard)
        self.btn_threshold_config.setEnabled(enable)
        self.btn_pause.setEnabled(enable)
        self.btn_record.setEnabled(enable)
        self.btn_open.setEnabled(enable)

    '''
    Event is fired, when the Arduino connection for the recording is up or failed to setup
    '''
    def worker_record_finished(self):
        self.enable_PDR_UI(True)

        if(self.worker_threshold.arduino_connect):
            self.PDR.connect_new_data_event(self.file_saver.on_new_data)
            self.PDR.clear_arrays()
            self.update_timer.start()
            self.update_plot()

    '''
    Connects to the Arduino and starts the timer, which updates the plot every x milliseconds .
    (the update interval is defined in __init__).
    '''
    def on_record_button(self) -> None:
        self.worker_threshold = connect_to_Arduino_Thread(self, True, 10000)
        self.worker_threshold.finished.connect(self.worker_record_finished)
        self.enable_PDR_UI(False)
        self.worker_threshold.start()

    '''
    Event is fired, when the Arduino connection for the threshold determination is up or failed to setup
    '''
    def worker_threshold_finished(self):
        self.enable_PDR_UI(True, True)
        
        if(self.worker_threshold.arduino_connect):
            self.update_timer.start()
            self.threshold_timer.start()
            self.update_plot()
            self.btn_threshold_config.setText("Übernehmen")
            self.btn_threshold_discard.setEnabled(True)

    '''
    Proposes a Threshold and writes it to the determined Threshold to the Threshold-Textbox
    '''
    def on_threshold_button(self) -> None:
        if self.threshold_timer.isActive() == False:
            self.worker_threshold = connect_to_Arduino_Thread(self, False, 1000)
            self.worker_threshold.finished.connect(self.worker_threshold_finished)
            self.enable_PDR_UI(False)
            self.worker_threshold.start()
        else:
            self.update_timer.stop()
            self.threshold_timer.stop()
            self.btn_threshold_config.setText("Testen")
            self.btn_threshold_discard.setEnabled(False)
            self.threshold.setText(str(max(self.PDR.y_values_envlope)))
            
    '''
    Stops the Threshold testing, without writing the determined Threshold to the Threshold-Textbox
    '''
    def on_threshold_discard_button(self) -> None:
        self.update_timer.stop()
        self.threshold_timer.stop()
        self.btn_threshold_config.setText("Testen")
        self.btn_threshold_discard.setEnabled(False)

    '''
    Stop the graph update timer.
    Also stop to save new data with the file_saver.
    '''
    def on_pause_button(self) -> None:
        self.update_timer.stop()
        
        # disconnect FileSaver-listener
        if hasattr(self, "PDR"):
            self.PDR.disconnect_new_data_event(self.file_saver.on_new_data)

    '''
    Shows the Save File Dialoge.
    '''
    def on_save_button(self) -> None:
        self.on_pause_button()
        self.file_saver.show_save_dialoge()

    '''
    Tries to open a csv that should contain a previous recording
    '''
    def on_open_button(self) -> None:
        
        file_selection = QFileDialog.getOpenFileName(self, "Alte Messung wählen", "", "Messungen (*.csv)")
        
        if file_selection[0].endswith(".csv"):
            try:
                fileopener = FileOpener.FileOpener(file_selection[0])
                fileopener.show_open_dialoge()
                fileopener.file_dialog.connect_close(self.on_fileopener_close)
                
                self.fileopener.append(fileopener) # append it to self, so it wont be disposed after this function
            except:
                msgBox = QMessageBox()
                msgBox.setText("Die Datei konnte nicht gelesen werden.")
                msgBox.exec()

    '''
    Event is fired, when a fileopener is closed
    '''
    def on_fileopener_close(self):
        # search for the closed fileopeners and remove them from the list, so the objects will be disposed
        indecies = []
        for i in range(0, len(self.fileopener)):
            if self.fileopener[i].file_dialog.closed:
                indecies.append(i)

        for i in indecies:
            self.fileopener.pop(i)
                


'''
Tries to open the Arduino-connection and sets arduino_connect = true, if one was opened.
Doing this in a new thread is necessary, since it involves a few seconds of busy-waiting and we want to keep the ui responsive.
'''
class connect_to_Arduino_Thread(QThread):

    '''
    arr_len is passed to PiDataReceiver.__init__
    send_threshold = True passes the threshold text in the MainWindow to PiDataReceiver.__init__
    main_window should be the MainWindow-instance, since it is the parent of this thread
    '''
    def __init__(self, main_window : MainWindow, send_threshold, arr_len) -> None:
        self.arduino_connect = False
        self.send_threshold = send_threshold
        self.mw = main_window
        self.arr_len = arr_len
        super().__init__(parent=main_window)

    def run(self) -> None:
        # open connection to Arduino
        try:
            if hasattr(self.mw, "PDR"):
                self.mw.PDR.before_delete()
                del self.mw.PDR
                    
            if self.send_threshold:
                self.mw.PDR = PDR.PiDataReceiver(port = self.mw.cbx_port.currentData(), threshold = int(self.mw.threshold.text()), arr_len = self.arr_len)
            else:
                self.mw.PDR = PDR.PiDataReceiver(port = self.mw.cbx_port.currentData(), threshold = 0, arr_len = self.arr_len)

            # wait for PDR to confirm, that the arduino is on that port
            while self.mw.PDR.thread_running and self.mw.PDR.port_confirmed == False:
                pass

            if self.mw.PDR.thread_running and self.mw.PDR.port_confirmed:
                self.arduino_connect = True
            else:
                if hasattr(self.mw, "PDR"):
                    self.mw.PDR.before_delete()
                    del self.mw.PDR
                self.arduino_connect = False

        except:
            if hasattr(self.mw, "PDR"):
                self.mw.PDR.before_delete()
                del self.mw.PDR
            self.arduino_connect = False

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
