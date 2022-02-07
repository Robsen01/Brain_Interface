import sys

sys.path.append('../../Brain_Interface')

from FileExport.FileDialog import FileDialog
from PySide2.QtWidgets import QFileDialog, QMessageBox
import ArduinoToPiDataTransfer.PiDataReceiverGeneric as PDRG
import tempfile
import os
import datetime

'''
Expects the user to hook its on_new_data event to the event, where the new data appears.
This data is saved to temp-files.
'''
class FileSaver:
    
    '''
    int_byte_len is the length of bytes used to represent one integer in the binary-files.
    max_displayed_values is the maximal number of Values that the Graph will display.
    '''
    def __init__(self, send_raw_data = True, send_filtered_data = True, send_envlope = True, int_byte_len = 8, max_displayed_values = 1000000):
        
        self.send_raw_data = send_raw_data
        self.send_filtered_data = send_filtered_data
        self.send_envlope = send_envlope

        self.max_displayed_values = max_displayed_values

        # length of bytes used to represent one integer in the binary-files
        self.int_byte_len = int_byte_len
        
        self.open_tmp_files()

        self.file_save_dialog = FileDialog()

        self.file_save_dialog.btn_save.clicked.connect(self.save_to_file)
        self.file_save_dialog.rdb_save_raw.clicked.connect(self.on_rdb_raw)
        self.file_save_dialog.rdb_save_filtered.clicked.connect(self.on_rdb_filtered)
        self.file_save_dialog.rdb_save_envlope.clicked.connect(self.on_rdb_envlope)
        
        self.file_save_dialog.btn_next_values.setVisible(False)
        self.file_save_dialog.btn_prev_values.setVisible(False)

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
    deletes old tempfiles and starts new ones
    '''
    def reset_tmp_files(self) -> None:
        self.close_tmp_files()
        self.open_tmp_files()

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
        self.update_plot(raw=False, filtered=False, envlope=True)

    '''
    Radio button event, when it is clicked. Shows the raw data in the plot.
    '''
    def on_rdb_raw(self):
        self.update_plot(raw=True, filtered=False, envlope=False)

    '''
    Radio button event, when it is clicked. Shows the filtered data in the plot.
    '''
    def on_rdb_filtered(self):
        self.update_plot(raw=False, filtered=True, envlope=False)

    '''
    Radio button event, when it is clicked. Shows the envlope data in the plot.
    '''
    def on_rdb_envlope(self):
        self.update_plot(raw=False, filtered=False, envlope=True)

    '''
    Show the plot with either the raw, filtered or envlope data.
    Only one of the Parameters should be true.
    '''
    def update_plot(self, raw = False, filtered = False, envlope = True):
        # read the files and preserve the filepositions from before
        x = []
        y = []
        
        self.temp_time.flush()
        temp_y_file = 0

        if raw:
            temp_y_file = self.temp_raw
        elif filtered:
            temp_y_file = self.temp_filtered
        else:
            temp_y_file = self.temp_envlope

        temp_y_file.flush()

        time_pos = self.temp_time.tell()
        y_file_pos = temp_y_file.tell()
        
        i = 0
        self.temp_time.seek(0)
        while i < self.max_displayed_values:
            bytex = self.temp_time.read(self.int_byte_len)
            if not bytex:
                # eof
                break
            x.append(
                PDRG.PiDataReceiverGeneric.time_to_s(
                    int.from_bytes(bytex, byteorder="big", signed = True)))
            i = i + 1

        i = 0
        temp_y_file.seek(0)
        while i < self.max_displayed_values:
            bytey = temp_y_file.read(self.int_byte_len)
            if not bytey:
                # eof
                break

            if raw:
                y.append(
                    PDRG.PiDataReceiverGeneric.raw_to_mV(
                        int.from_bytes(bytey, byteorder="big", signed = True)))
            elif filtered:
                y.append(
                    PDRG.PiDataReceiverGeneric.filtered_to_mV(
                        int.from_bytes(bytey, byteorder="big", signed = True)))
            else:
                y.append(int.from_bytes(bytey, byteorder="big", signed = True))
            
            i = i + 1

        self.temp_time.seek(time_pos)
        temp_y_file.seek(y_file_pos)

        # plot the new data
        self.file_save_dialog.canvas.axes.cla()
        
        self.file_save_dialog.canvas.axes.plot(x, y, 'r')
        if raw:
            self.file_save_dialog.canvas.axes.set_title("Rohdaten")
            self.file_save_dialog.canvas.axes.set_ylabel('(mV)')
        elif filtered:
            self.file_save_dialog.canvas.axes.set_title("gefiltert (mV)")
            self.file_save_dialog.canvas.axes.set_ylabel('(mV)')
        else:
            self.file_save_dialog.canvas.axes.set_title("envelope")

        self.file_save_dialog.canvas.axes.set_xlabel('Zeit (s)')
        self.file_save_dialog.canvas.draw()

    '''
    Savebtn Event.
    Saves the selected data (raw, filtered, envelope) and timestamp to csv
    '''
    def save_to_file(self, event):
        # open file Dialoge
        dtt_now = datetime.datetime.now()
        dtt_string = dtt_now.strftime("%Y%m%d_%H%M%S")

        if self.file_save_dialog.rdb_save_raw.isChecked():
            dtt_string += "_rohdaten"
        elif self.file_save_dialog.rdb_save_filtered.isChecked():
            dtt_string += "_gefilterte"
        else:
            dtt_string += "_envelope"
        
        file_selection = QFileDialog.getSaveFileName(self.file_save_dialog, "Speicherposition wählen", dtt_string, "Messungen (*.csv)")
        
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
                pos_envlope = self.temp_envlope.tell()

                self.temp_time.seek(0)
                self.temp_raw.seek(0)
                self.temp_filtered.seek(0)
                self.temp_envlope.seek(0)

                file_ok = True
                if self.file_save_dialog.chk_accumulate.isChecked():
                    file_ok = self.save_cumulate(file)
                else:
                    self.save_dont_cumulate(file)
                
                self.temp_time.seek(pos_time)
                self.temp_raw.seek(pos_raw)
                self.temp_filtered.seek(pos_filtered)
                self.temp_envlope.seek(pos_envlope)

                file.close()
                
                # if the kommulieren-textfield had a bad value
                if not file_ok:
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
    def save_dont_cumulate(self, file) -> None:

        file.write("Zeitpunkt (s)")
        
        if self.file_save_dialog.rdb_save_raw.isChecked():
            file.write(",Rohdaten (mV)")
        if self.file_save_dialog.rdb_save_filtered.isChecked():
            file.write(",gefilterte Daten (mV)")
        if self.file_save_dialog.rdb_save_envlope.isChecked():
            file.write(",envelope")
        file.write("\n")

        while True:
            byte_time = self.temp_time.read(self.int_byte_len)
            if not byte_time:
                # eof
                break
            
            file.write(str(
                PDRG.PiDataReceiverGeneric.time_to_s(
                    int.from_bytes(byte_time, byteorder="big", signed = True))))

            if self.file_save_dialog.rdb_save_raw.isChecked():
                byte_raw = self.temp_raw.read(self.int_byte_len)
                file.write("," + str(
                    PDRG.PiDataReceiverGeneric.raw_to_mV(
                        int.from_bytes(byte_raw, byteorder="big", signed = True))))

            if self.file_save_dialog.rdb_save_filtered.isChecked():
                byte_filtered = self.temp_filtered.read(self.int_byte_len)
                file.write("," + str(
                    PDRG.PiDataReceiverGeneric.filtered_to_mV(
                        int.from_bytes(byte_filtered, byteorder="big", signed = True))))

            if self.file_save_dialog.rdb_save_envlope.isChecked():
                byte_envlope = self.temp_envlope.read(self.int_byte_len)
                file.write("," + str(int.from_bytes(byte_envlope, byteorder="big", signed = True)))

            file.write("\n")

    '''
    Save the data cumulated. The accumulation step-size is in the Dialogs Textbox.
    '''
    def save_cumulate(self, file) -> bool:
        time_cumulate = 0
        time_step = -1
        time_next = -1
        values = 0
        summed_raw = 0
        summed_filtered = 0
        summed_envlope = 0

        # check cumulate value
        if self.file_save_dialog.chk_accumulate.isChecked():
            try:
                # *1000000 to convert seconds to nanoseconds
                time_cumulate = float(self.file_save_dialog.txt_cumulate.text().replace(",", "."))*1000000
            except:
                msgBox = QMessageBox()
                msgBox.setText("Konnte das Textfeld kommulieren nicht auslesen.\nBitte geben sie eine ganze Zahl z.B. 1 oder gleitkommazahl z.B.1,1 ein.")
                msgBox.exec()
                return False

        file.write("Zeitpunkt (s)")

        if self.file_save_dialog.rdb_save_raw.isChecked():
            file.write(",Rohdaten (mV)")

        if self.file_save_dialog.rdb_save_filtered.isChecked():
            file.write(",gefilterte Daten (mV)")

        if self.file_save_dialog.rdb_save_envlope.isChecked():
            file.write(",envelope")

        file.write("\n")

        while True:
            byte_time = self.temp_time.read(self.int_byte_len)
            
            if not byte_time:
                # eof
                break
            time = int.from_bytes(byte_time, byteorder="big", signed = True)
            
            if time_step == -1:
                time_step = time
                time_next = time_step + time_cumulate

            if time_next > time:
                # cummulate, while the next time step is not reached
                values = values + 1
        
                if self.file_save_dialog.rdb_save_raw.isChecked():
                    byte_raw = self.temp_raw.read(self.int_byte_len)
                    summed_raw = summed_raw + int.from_bytes(byte_raw, byteorder="big", signed = True)

                if self.file_save_dialog.rdb_save_filtered.isChecked():
                    byte_filtered = self.temp_filtered.read(self.int_byte_len)
                    summed_filtered = summed_filtered + int.from_bytes(byte_filtered, byteorder="big", signed = True)

                if self.file_save_dialog.rdb_save_envlope.isChecked():
                    byte_envlope = self.temp_envlope.read(self.int_byte_len)
                    summed_envlope = summed_envlope + int.from_bytes(byte_envlope, byteorder="big", signed = True)
            else:
                # we reached the next timestep. Write the values to file
                file.write(str(PDRG.PiDataReceiverGeneric.time_to_s(time_step)))
                
                if self.file_save_dialog.rdb_save_raw.isChecked():
                    byte_raw = self.temp_raw.read(self.int_byte_len)
                    file.write("," + str(
                        PDRG.PiDataReceiverGeneric.raw_to_mV(summed_raw/values)))

                if self.file_save_dialog.rdb_save_filtered.isChecked():
                    byte_filtered = self.temp_filtered.read(self.int_byte_len)
                    file.write("," + str(
                        PDRG.PiDataReceiverGeneric.filtered_to_mV(summed_filtered/values)))

                if self.file_save_dialog.rdb_save_envlope.isChecked():
                    byte_envlope = self.temp_envlope.read(self.int_byte_len)
                    file.write("," + str(summed_envlope/values))

                file.write("\n")

                # start to cummulate the first values of the next step
                values = 1
                time_step = time_next
                time_next = time_next + time_cumulate

                if self.file_save_dialog.rdb_save_raw.isChecked():
                    byte_raw = self.temp_raw.read(self.int_byte_len)
                    summed_raw = int.from_bytes(byte_raw, byteorder="big", signed = True)

                if self.file_save_dialog.rdb_save_filtered.isChecked():
                    byte_filtered = self.temp_filtered.read(self.int_byte_len)
                    summed_filtered =  int.from_bytes(byte_filtered, byteorder="big", signed = True)

                if self.file_save_dialog.rdb_save_envlope.isChecked():
                    byte_envlope = self.temp_envlope.read(self.int_byte_len)
                    summed_envlope =  int.from_bytes(byte_envlope, byteorder="big", signed = True)
        return True