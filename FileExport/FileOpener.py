import sys

from numpy import sign, string_
sys.path.append('../../Brain_Interface')

from FileExport.FileDialog import FileDialog
from PySide2.QtWidgets import QFileDialog, QMessageBox
import tempfile
import os

'''
Expects the user to hook its on_new_data event to the event, where the new data appears.
This data is saved to temp-files.
'''
class FileOpener:
    
    '''
    int_byte_len is the length of bytes used to represent one integer in the binary-files.
    max_displayed_values is the maximal number of Values that the Graph will display.
    '''
    def __init__(self, filename, max_displayed_values = 100000):
        
        self.max_displayed_values = max_displayed_values

        self.file = open(filename, "r")

        self.header = self.file.readline().strip().split(",") # read the header line
        self.values = []
        
        for s in self.header:
            self.values.append([])
        
        self.file_header_end = self.file.tell() # necessary, when we read the file from back to front

        self.read_file(max_displayed_values)

        self.file_dialog = FileDialog()
        # self.file_dialog.settings_group.setHidden(True)

    '''
    Opens the FileSaveDialog-Window.
    '''
    def show_open_dialoge(self):
        self.file_dialog.show()
        self.update_plot()

    '''
    Read the next x lines of the file. if the arrays are full, the first values are dropped.
    '''
    def read_file(self, lines : int):
        i = 0
        while i < lines:
            line = self.file.readline()
            
            if not line:
                # eof
                break
            
            lst = line.strip().split(",")
            
            for i in range(0, len(lst)):
                if len(self.values[i]) > self.max_displayed_values:
                    self.values[i].pop(0)
                
                self.values[i].append(float(lst[i]))

    '''
    Draw the Plot.
    '''
    def update_plot(self):
        self.file_dialog.canvas.axes.cla()  # Clear the canvas.

        # TODO achsen beschriften und alle values[2],[3] anzeigen
        self.file_dialog.canvas.axes.plot(self.values[0], self.values[1], 'r')
        # Trigger the canvas to update and redraw.
        self.file_dialog.canvas.draw()