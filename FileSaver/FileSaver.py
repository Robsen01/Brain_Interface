import sys

from numpy import sign
sys.path.append('../../Brain_Interface')

from FileSaver.FileSaveDialog import FileSaveDialog

import os
import struct

"""
    expects the user to hook its on_new_data event to the event, where the new data appears.
    this data is saved to a temp-file
"""
class FileSaver:
    def __init__(self, allow_pickle = False, send_raw_data = True, send_filtered_data = True, send_envlope = True, int_byte_len = 8, max_displayed_values = 100000):
        self.allow_pickle = allow_pickle
        # create tmp file
        # self.temp = tempfile.TemporaryFile()
        self.tmp_time_name = "~temptime"
        self.tmp_raw_name = "~tempraw"
        self.tmp_filtered_name = "~tempfiltered"
        self.tmp_envlope_name = "~tempenvlope"

        self.send_raw_data = send_raw_data
        self.send_filtered_data = send_filtered_data
        self.send_envlope = send_envlope

        self.max_displayed_values = max_displayed_values

        self.int_byte_len = 32
        
        self.remove_tmp_files()

        self.open_tmp_files()

        self.file_save_dialog = FileSaveDialog()

    def __del__(self):
        # delete tmp file
        self.remove_tmp_files()

    def remove_tmp_files(self):
        try:
            self.close_tmp_files()
            os.remove(self.tmp_time_name)
            os.remove(self.tmp_raw_name)
            os.remove(self.tmp_filtered_name)
            os.remove(self.tmp_envlope_name)
        except OSError:
            
            pass

    def open_tmp_files(self, mode = "ab") -> None:
        self.temp_time = open(self.tmp_time_name, mode)
        if self.send_raw_data:
            self.temp_raw = open(self.tmp_raw_name, mode)
        if self.send_filtered_data:
            self.temp_filtered = open(self.tmp_filtered_name, mode)
        if self.send_envlope:
            self.temp_envlope = open(self.tmp_envlope_name, mode)

    def close_tmp_files(self) -> None:
        if hasattr(self, "temp_time"):
            self.temp_time.close()
            if self.send_raw_data:
                self.temp_raw.close()
            if self.send_filtered_data:
                self.temp_filtered.close()
            if self.send_envlope:
                self.temp_envlope.close()

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
            # self.tempenvelope.write(data[len(data)-2])
            # np.save(self.f, arr)#allow_pickle=self.allow_pickle)

    def show_save_dialoge(self):
        self.file_save_dialog.show()
        self.update_plot()

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