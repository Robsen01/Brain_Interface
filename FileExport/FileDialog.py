import sys
from PySide2.QtGui import QValidator
sys.path.append('../../Brain_Interface')

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PySide2.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QGroupBox, QCheckBox, QPushButton, QLineEdit, QGridLayout, QRadioButton
import sys
import matplotlib

matplotlib.use('Qt5Agg')

'''
Canvas, which draws the Graph that shows the Data.
'''
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

'''
Window, which holds the Graph and Controls.
'''
class FileDialog(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(FileDialog, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()

        self.setup_graph_group()
        self.setup_settings_group()
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.closed = True
        self.onclose = -1

    '''
    Setup the first Groupbox, which holds the Graph and the Graph-controls.
    '''
    def setup_graph_group(self) -> None:
        graph_group = QGroupBox()
        graph_layout = QGridLayout()

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        graph_layout.addWidget(self.canvas, 2, 1, 1, 3)
        
        toolbar = NavigationToolbar(self.canvas, self)
        graph_layout.addWidget(toolbar, 1, 1, 1, 1)

        self.btn_prev_values = QPushButton("<<")
        graph_layout.addWidget(self.btn_prev_values, 1, 2, 1, 1)

        self.btn_next_values = QPushButton(">>")
        graph_layout.addWidget(self.btn_next_values, 1, 3, 1, 1)

        graph_group.setLayout(graph_layout)
        self.layout.addWidget(graph_group)                
    
    '''
    Setup the second Groupbox, which holds the save-settings.
    '''
    def setup_settings_group(self) -> None:
        self.settings_group = QGroupBox(title="Zu Speichernde Daten")

        settings_layout = QHBoxLayout()
        self.settings_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        self.rdb_save_raw = QRadioButton(text = "Rohdaten")
        self.rdb_save_raw.setChecked(False)
        settings_layout.addWidget(self.rdb_save_raw)

        self.rdb_save_filtered = QRadioButton(text = "gefilterte Daten")
        self.rdb_save_filtered.setChecked(False)
        settings_layout.addWidget(self.rdb_save_filtered)

        self.rdb_save_envlope = QRadioButton(text = "envelope")
        self.rdb_save_envlope.setChecked(True)
        settings_layout.addWidget(self.rdb_save_envlope)

        self.chk_accumulate  = QCheckBox(text = "kumuliert")
        self.chk_accumulate .setChecked(True)
        settings_layout.addWidget(self.chk_accumulate)

        self.txt_cumulate  = QLineEdit()
        self.txt_cumulate.setText("0,2")
        settings_layout.addWidget(self.txt_cumulate)

        self.btn_save = QPushButton(text = "Speichern")
        settings_layout.addWidget(self.btn_save)

        self.settings_group.setLayout(settings_layout)
        self.layout.addWidget(self.settings_group) 

    '''
    called when the Window is closed with the cross-button in the corner
    '''
    def closeEvent(self, event) -> None:
        self.closed = True
        if self.onclose != -1:
            self.onclose()
        return super().closeEvent(event)
        
    def show(self) -> None:
        self.closed = False
        return super().show()

    '''
    connects the function to the call of the close funktion
    '''
    def connect_close(self, event):
        self.onclose = event


def main():
    app = QApplication(sys.argv)
    w = FileDialog()
    w.show()
    ret = app.exec_()
    sys.exit(ret)
    

if __name__ == '__main__':
    main()
