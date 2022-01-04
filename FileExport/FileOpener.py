import sys

sys.path.append('../../Brain_Interface')

from FileExport.FileDialog import FileDialog
import math

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

        self.file_dialog = FileDialog()
        self.file_dialog.settings_group.setHidden(True)
        
        self.file_dialog.btn_prev_values.clicked.connect(self.on_prev_values)
        self.file_dialog.btn_prev_values.setEnabled(False)
        self.file_dialog.btn_next_values.clicked.connect(self.on_next_values)

        self.file = open(filename, "r")

        self.header = self.file.readline().strip().split(",") # read the header line
        self.values = []
        
        for s in self.header:
            self.values.append([])
        
        # stores file pointer value history after every next-values-btn click
        self.plot_history = [self.file.tell()]

        if self.file_read(math.floor(max_displayed_values / 2)):
            self.file_dialog.btn_next_values.setEnabled(False)
        
        self.plot_history.append(self.file.tell())

        if self.file_read(max_displayed_values - math.floor(max_displayed_values / 2)):
            self.file_dialog.btn_next_values.setEnabled(False)

        
    '''
    Is fired, when the prev_values-button is clicked.
    Reads and shos the previous floor(max_displayed_values / 2) values if any are available.
    '''
    def on_prev_values(self, event = None) -> None:
        if len(self.plot_history) > 0:
            # set the file pointer to the previous start position and read max_displayed_values lines
            prevstart = self.plot_history[len(self.plot_history)-3]
            self.plot_history.pop()
            self.file.seek(prevstart)
            self.file_read(self.max_displayed_values)
            self.update_plot()
            self.file_dialog.btn_next_values.setEnabled(True)

        if len(self.plot_history) == 2:
            self.file_dialog.btn_prev_values.setEnabled(False)

    '''
    Is fired, when the next_values-button is clicked.
    Reads and shows the next floor(max_displayed_values / 2) values if any are available.
    '''
    def on_next_values(self, event = None) -> None:
        self.plot_history.append(self.file.tell())
        self.file_dialog.btn_prev_values.setEnabled(True)
        
        if self.file_read(math.floor(self.max_displayed_values / 2)):
            #if end of file
            self.file_dialog.btn_next_values.setEnabled(False)

        self.update_plot()

    '''
    Opens the FileSaveDialog-Window.
    '''
    def show_open_dialoge(self):
        self.file_dialog.show()
        self.update_plot()

    '''
    Read the next x lines of the file. if the arrays are full, the first values are dropped.
    Returns true, if end of file was reached.
    '''
    def file_read(self, lines : int) -> bool:
        eof = False
        
        for l in range(0, lines):
            line = self.file.readline()
            
            if not line:
                eof = True
                break
            
            lst = line.strip().split(",")
            
            for j in range(0, len(lst)):
                if len(self.values[j]) == self.max_displayed_values:
                    self.values[j].pop(0)
                
                self.values[j].append(float(lst[j]))

            
        return eof

    '''
    Draw the Plot.
    '''
    def update_plot(self):
        self.file_dialog.canvas.axes.cla()  # Clear the canvas.

        # TODO achsen beschriften
        self.file_dialog.canvas.axes.plot(self.values[0], self.values[1], 'r')
        # Trigger the canvas to update and redraw.
        self.file_dialog.canvas.draw()
