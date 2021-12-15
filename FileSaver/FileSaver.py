import sys

from numpy import sign
sys.path.append('../../Brain_Interface')

from FileSaver.FileSaveDialog import FileSaveDialog
from PySide2.QtWidgets import QFileDialog, QMessageBox
import tempfile
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
        
        self.send_raw_data = send_raw_data
        self.send_filtered_data = send_filtered_data
        self.send_envlope = send_envlope

        self.max_displayed_values = max_displayed_values

        # length of bytes used to represent one integer in the binary-files
        self.int_byte_len = int_byte_len
        
        self.open_tmp_files()

        self.file_save_dialog = FileSaveDialog()

        self.file_save_dialog.btn_save.clicked.connect(self.save_to_file)

    '''
    Openes all the temp-files. Mode is append and read binary.
    '''
    def open_tmp_files(self) -> None:
        self.temp_time = tempfile.TemporaryFile(mode="ab+")
        if self.send_raw_data:
            self.temp_raw = tempfile.TemporaryFile(mode="ab+")
        if self.send_filtered_data:
            self.temp_filtered = tempfile.TemporaryFile(mode="ab+")
        if self.send_envlope:
            self.temp_envlope = tempfile.TemporaryFile(mode="ab+")

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

        # self.close_tmp_files()
        # self.open_tmp_files(mode="rb")
        x = []
        y = []
        
        # read the files and save the filepositions before
        self.temp_time.flush()
        self.temp_envlope.flush()

        time_pos = self.temp_time.tell()
        envlope_pos = self.temp_time.tell()
        
        i = 0
        self.temp_time.seek(0)
        while i < self.max_displayed_values:
            bytex = self.temp_time.read(self.int_byte_len)
            if not bytex:
                # eof
                break
            x.append(int.from_bytes(bytex, byteorder="big", signed = True))
            i = i + 1

        i = 0
        self.temp_envlope.seek(0)
        while i < self.max_displayed_values:
            bytey = self.temp_envlope.read(self.int_byte_len)
            if not bytey:
                # eof
                break
            y.append(int.from_bytes(bytey, byteorder="big", signed = True))
            i = i + 1

        # set the filepositions to the old positions
        self.temp_time.seek(time_pos)
        self.temp_envlope.seek(envlope_pos)
        
        self.file_save_dialog.canvas.axes.plot(x, y, 'r')
        # Trigger the canvas to update and redraw.
        self.file_save_dialog.canvas.draw()

    '''
    Savebtn Event.
    Saves the selected data (raw, filtered, envelope) and timestamp to csv
    '''
    def save_to_file(self, event):
        # open file Dialoge
        file_selection = QFileDialog.getSaveFileName(self.file_save_dialog, "Speicherposition wählen", "", "Messungen (*.csv)")
        
        if file_selection[0].endswith(".csv"):
            try:
                file = open(file_selection[0], "w")
                # read the files and save the filepositions from before
                self.temp_time.flush()
                self.temp_raw.flush()
                self.temp_filtered.flush()
                self.temp_envlope.flush()

                pos_time = self.temp_time.tell()
                pos_raw = self.temp_raw.tell()
                pos_filtered = self.temp_filtered.tell()
                pos_envlope = self.temp_time.tell()

                self.temp_time.seek(0)
                self.temp_raw.seek(0)
                self.temp_filtered.seek(0)
                self.temp_envlope.seek(0)

                accumulated_ok = False
                if self.file_save_dialog.chk_accumulate.isChecked():
                    accumulated_ok = self.save_accumulate(file)
                else:
                    self.save_dont_accumulate(file)
                
                # set the filepositions to the old positions
                self.temp_time.seek(pos_time)
                self.temp_raw.seek(pos_raw)
                self.temp_filtered.seek(pos_filtered)
                self.temp_envlope.seek(pos_envlope)

                file.close()
                
                if not accumulated_ok:
                    os.remove(file_selection[0])

            except:
                msgBox = QMessageBox()
                msgBox.setText("Fehler während des Speicherns.")
                msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Bitte wählen Sie eine .csv Datei.")
            msgBox.exec()

    '''
    Save the data without accumulating timesteps.
    '''    
    def save_dont_accumulate(self, file) -> None:

        file.write("Zeitpunkt (s)")
        
        if self.file_save_dialog.chk_save_raw.isChecked():
            file.write(",Rohdaten")
        if self.file_save_dialog.chk_save_filtered.isChecked():
            file.write(",gefilterte Daten")
        if self.file_save_dialog.chk_save_envlope.isChecked():
            file.write(",gefilterte quadriert")
        file.write("\n")

        while True:
            byte_time = self.temp_time.read(self.int_byte_len)
            if not byte_time:
                # eof
                break
            
            file.write(str(int.from_bytes(byte_time, byteorder="big", signed = True)/1000000))

            if self.file_save_dialog.chk_save_raw.isChecked():
                byte_raw = self.temp_raw.read(self.int_byte_len)
                file.write("," + str(int.from_bytes(byte_raw, byteorder="big", signed = True)))
            if self.file_save_dialog.chk_save_filtered.isChecked():
                byte_filtered = self.temp_filtered.read(self.int_byte_len)
                file.write("," + str(int.from_bytes(byte_filtered, byteorder="big", signed = True)))
            if self.file_save_dialog.chk_save_envlope.isChecked():
                byte_envlope = self.temp_envlope.read(self.int_byte_len)
                file.write("," + str(int.from_bytes(byte_envlope, byteorder="big", signed = True)))
            file.write("\n")

    '''
    Save the data accumulated. The accumulation step-size is in the Dialogs Textbox.
    '''
    def save_accumulate(self, file) -> bool:
        time_accumulate = 0
        time_step = -1
        time_next = -1
        values = 0
        summed_raw = 0
        summed_filtered = 0
        summed_envlope = 0

        # check accumulate value
        if self.file_save_dialog.chk_accumulate.isChecked():
            try:
                # *1000000 to convert seconds to nanoseconds
                time_accumulate = float(self.file_save_dialog.txt_accumulate.text().replace(",", "."))*1000000
            except:
                msgBox = QMessageBox()
                msgBox.setText("Konnte das Textfeld kommulieren nicht auslesen.\nBitte geben sie eine ganze Zahl z.B. 1 oder gleitkommazahl z.B.1,1 ein.")
                msgBox.exec()
                return False

        file.write("Zeitpunkt (s)")

        if self.file_save_dialog.chk_save_raw.isChecked():
            file.write(",Rohdaten")
        if self.file_save_dialog.chk_save_filtered.isChecked():
            file.write(",gefilterte Daten")
        if self.file_save_dialog.chk_save_envlope.isChecked():
            file.write(",gefilterte quadriert")
        file.write("\n")

        while True:
            byte_time = self.temp_time.read(self.int_byte_len)
            
            if not byte_time:
                # eof
                break
            time = int.from_bytes(byte_time, byteorder="big", signed = True)
            
            if time_step == -1:
                time_step = time
                time_next = time_step + time_accumulate

            if time_next > time:
                values = values + 1
        
                if self.file_save_dialog.chk_save_raw.isChecked():
                    byte_raw = self.temp_raw.read(self.int_byte_len)
                    summed_raw = summed_raw + int.from_bytes(byte_raw, byteorder="big", signed = True)
                if self.file_save_dialog.chk_save_filtered.isChecked():
                    byte_filtered = self.temp_filtered.read(self.int_byte_len)
                    summed_filtered = summed_filtered + int.from_bytes(byte_filtered, byteorder="big", signed = True)
                if self.file_save_dialog.chk_save_envlope.isChecked():
                    byte_envlope = self.temp_envlope.read(self.int_byte_len)
                    summed_envlope = summed_envlope + int.from_bytes(byte_envlope, byteorder="big", signed = True)
            else:
                file.write(str(time_step/1000000))
                
                if self.file_save_dialog.chk_save_raw.isChecked():
                    byte_raw = self.temp_raw.read(self.int_byte_len)
                    file.write("," + str(summed_raw/values))
                if self.file_save_dialog.chk_save_filtered.isChecked():
                    byte_filtered = self.temp_filtered.read(self.int_byte_len)
                    file.write("," + str(summed_filtered/values))
                if self.file_save_dialog.chk_save_envlope.isChecked():
                    byte_envlope = self.temp_envlope.read(self.int_byte_len)
                    file.write("," + str(summed_envlope/values))
                file.write("\n")

                values = 0
                time_step = time_next
                time_next = time_next + time_accumulate

                if self.file_save_dialog.chk_save_raw.isChecked():
                    byte_raw = self.temp_raw.read(self.int_byte_len)
                    summed_raw = int.from_bytes(byte_raw, byteorder="big", signed = True)
                if self.file_save_dialog.chk_save_filtered.isChecked():
                    byte_filtered = self.temp_filtered.read(self.int_byte_len)
                    summed_filtered =  int.from_bytes(byte_filtered, byteorder="big", signed = True)
                if self.file_save_dialog.chk_save_envlope.isChecked():
                    byte_envlope = self.temp_envlope.read(self.int_byte_len)
                    summed_envlope =  int.from_bytes(byte_envlope, byteorder="big", signed = True)
        return True