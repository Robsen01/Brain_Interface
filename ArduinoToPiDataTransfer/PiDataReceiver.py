import sys
sys.path.append('../Brain_Interface')
sys.path.append('../UserInterface')
import ArduinoToPiDataTransfer.PiDataReceiverGeneric as PDRG
from threading import Thread
import time

'''
PiDataReceiver is a subclass of PiDataReceiverGeneric.
It reads the Arduino-data and keeps it in arrays for you.
It also initializes the Arduino-Connection for you.
It also raises Events to connected Listeners, when new Data arrives.
'''
class PiDataReceiver(PDRG.PiDataReceiverGeneric):
    '''
    This Class initializes the arduino communication. 
    It also starts a thread that reads y.
    port must be a string like 'COM3'. Retrieve possible ports with PiDataReceiver.list_possible_ports.
    An arr_len of 10000 stores values of roughly 20 seconds
    '''
    def __init__(self, port, threshold, arr_len = 10000) -> None:
        
        super().__init__(port, threshold=threshold, baudrate=115200, timeout=.1, send_raw_data = True, send_filtered_data = True, send_envlope = True, data_separation=",")
        # 10000 values should store roughly 20 seconds
        self.arrlen = arr_len
        # fill with zeros, so the displayed Graph does not change in length while it fills
        self.x_queue = [0 for i in range(self.arrlen)]
        self.y_values_raw = [0 for i in range(self.arrlen)]
        self.y_values_filtered = [0 for i in range(self.arrlen)]
        self.y_values_envlope = [0 for i in range(self.arrlen)]
        self.thread = Thread(target = self.threaded_function, args = (1, ))
        
        # flag if thread is running = True
        self.thread_running = True
        # flag if arduino has confirmed its all good
        self.port_confirmed = False
        self.thread.start()
        self.write_data = True # true if the arriving data should be pushed in the value-arrays
        
        # array for new-data-event listener functions
        self.listeners = []


    '''
    Closes the arduino port and stops the read-data thread
    '''
    def before_delete(self):
        self.thread_running = False
        return super().close_arduino_port()

    '''
    After 3 seconds this thread initializes the arduino communication.
    After that it recieves the Arduino Data and writes it to the y_values_... arrays
    '''
    def threaded_function(self, arg) -> None:
        # need to wait 3 seconds here, to wait for arduino connection to set-up
        time.sleep(3)

        # stop the thread if there was no arduino at the given port
        if PDRG.PiDataReceiverGeneric.init_arduino(self):
            self.port_confirmed = True
        else:
            self.thread_running = False
            return
        
        while 1:
            lst = PDRG.PiDataReceiverGeneric.read(self)

            if(len(lst) == 4 and self.write_data):
                self.y_values_raw.pop(0)
                self.y_values_raw.append(PDRG.PiDataReceiverGeneric.raw_to_mV(lst[0]))
                self.y_values_filtered.pop(0)
                self.y_values_filtered.append(PDRG.PiDataReceiverGeneric.filtered_to_mV(lst[1]))
                self.y_values_envlope.pop(0)
                self.y_values_envlope.append(lst[2])
                self.x_queue.pop(0)
                self.x_queue.append(PDRG.PiDataReceiverGeneric.time_to_s(lst[3]))
            
            # signal data-listeners
            for func in self.listeners:
                func(lst)
            
            if not self.thread_running:
                return

    """
    Connect to Event so the given function is called when new data is recieved.
    The function will recieve one parameter, which is a list with the data.
    """
    def connect_new_data_event(self, connect_func) -> None:
        self.listeners.append(connect_func)

    """
    Disconnects the previously connected Event-function.
    """
    def disconnect_new_data_event(self, connect_func) -> None:
        if self.listeners.count(connect_func) > 0:
            self.listeners.remove(connect_func)

    def clear_arrays(self, x_queue = True, y_values_raw_data = True, y_values_filtered_data = True, y_values_envlope = True) -> None:
        if x_queue == True:
            self.x_queue = [0 for i in range(self.arrlen)]
        if y_values_raw_data == True:
            self.y_values_raw = [0 for i in range(self.arrlen)]
        if y_values_filtered_data == True:
            self.y_values_filtered = [0 for i in range(self.arrlen)]
        if y_values_envlope == True:
            self.y_values_envlope = [0 for i in range(self.arrlen)]