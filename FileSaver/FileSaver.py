import sys

from numpy import sign
sys.path.append('../../Brain_Interface')

from FileSaver.FileSaveDialog import FileSaveDialog
import os

'''
Expects the user to hook its on_new_data event to the event, where the new data appears.
This data is saved to temp-files.
'''
class FileSaver:
    
    '''
    int_byte_len is the length of bytes used to represent one integer in the binary-files.
    max_displayed_values is the maximal number of Values that the Graph will display.
    '''
    def __init__(self, send_raw_data = True, send_filtered_data = True, send_envlope = True, int_byte_len = 8, max_displayed_values = 100000):
        # names of the temp-files
        self.tmp_time_name = "~temptime"
        self.tmp_raw_name = "~tempraw"
        self.tmp_filtered_name = "~tempfiltered"
        self.tmp_envlope_name = "~tempenvlope"

        self.send_raw_data = send_raw_data
        self.send_filtered_data = send_filtered_data
        self.send_envlope = send_envlope

        self.max_displayed_values = max_displayed_values

        # length of bytes used to represent one integer in the binary-files
        self.int_byte_len = int_byte_len
        
        self.remove_tmp_files()

        self.open_tmp_files()

        self.file_save_dialog = FileSaveDialog()

    '''
    Deletes the temp-files, when this class is deleted.
    '''
    def __del__(self):
        # delete tmp file
        self.remove_tmp_files()

    '''
    Deletes the temp-files.
    '''
    def remove_tmp_files(self):
        try:
            self.close_tmp_files()
            os.remove(self.tmp_time_name)
            os.remove(self.tmp_raw_name)
            os.remove(self.tmp_filtered_name)
            os.remove(self.tmp_envlope_name)
        except OSError:
            print("could not delete the temp-files.")
            pass

    '''
    Openes all the temp-files.
    Mode defines the work-mode (read = rb or append = ab).
    '''
    def open_tmp_files(self, mode = "ab") -> None:
        self.temp_time = open(self.tmp_time_name, mode)
        if self.send_raw_data:
            self.temp_raw = open(self.tmp_raw_name, mode)
        if self.send_filtered_data:
            self.temp_filtered = open(self.tmp_filtered_name, mode)
        if self.send_envlope:
            self.temp_envlope = open(self.tmp_envlope_name, mode)

    '''
    Closes all the temp-files.
    '''
    def close_tmp_files(self) -> None:
        if hasattr(self, "temp_time"):
            self.temp_time.close()
            if self.send_raw_data:
                self.temp_raw.close()
            if self.send_filtered_data:
                self.temp_filtered.close()
            if self.send_envlope:
                self.temp_envlope.close()

    '''
    Event-Handler which should be connected to a Event wich is fired when new Data arrives.
    Expects the list of the Data.
    Writes this Data to the respective Temp-file.
    '''
    def on_new_data(self, data : list):
        if len(data)>0:
            i = 0
            if self.send_raw_data:
                self.temp_raw.write(data[i].to_bytes(self.int_byte_len, "big", signed = True))
                i = i+1
            if self.send_filtered_data:
                self.temp_filtered.write(data[i].to_bytes(self.int_byte_len, "big", signed = True))
                i = i+1
            if self.send_envlope:
                self.temp_envlope.write(data[i].to_bytes(self.int_byte_len, "big", signed = True))
                i = i+1

            self.temp_time.write(data[i].to_bytes(self.int_byte_len, "big", signed = True))

    '''
    Opens the FileSaveDialog-Window.
    '''
    def show_save_dialoge(self):
        self.file_save_dialog.show()
        self.update_plot()

    '''
    Draw the Plot.
    '''
    def update_plot(self):
        self.file_save_dialog.canvas.axes.cla()  # Clear the canvas.

        self.close_tmp_files()
        self.open_tmp_files(mode="rb")
        i = 0
        x = []
        y = []
        while i < self.max_displayed_values:
            bytex = self.temp_time.read(self.int_byte_len)
            if not bytex:
                # eof
                break
            x.append(int.from_bytes(bytex, byteorder="big", signed = True))

        while i < self.max_displayed_values:
            bytey = self.temp_envlope.read(self.int_byte_len)
            if not bytey:
                # eof
                break
            y.append(int.from_bytes(bytey, byteorder="big", signed = True))
        
        self.file_save_dialog.canvas.axes.plot(x, y, 'r')
        # Trigger the canvas to update and redraw.
        self.file_save_dialog.canvas.draw()