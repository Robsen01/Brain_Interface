import sys
sys.path.append('../Brain_Interface')
sys.path.append('../UserInterface')
import ArduinoToPiDataTransfer.PiDataReceiverGeneric as PDRG
from threading import Thread
import time
import numpy as np

class PiDataReceiver(PDRG.PiDataReceiverGeneric):
    '''
    port must be a string like 'COM3'. Retrieve possible ports with PiDataReceiver.list_possible_ports
    Also initializes the arduino communication. 
    Also starts a thread that reads y
    '''
    def __init__(self, port, threshold) -> None:
        
        super().__init__(port, threshold=threshold, baudrate=115200, timeout=.1, send_raw_data = True, send_filtered_data = True, send_envlope = True, data_separation=",")
        # 10000 values should store the 10 seconds
        arrlen = 10000
        self.x_queue = [0 for i in range(arrlen)]
        self.y_values_send_raw_data = [0 for i in range(arrlen)]
        self.y_values_send_filtered_data = [0 for i in range(arrlen)]
        self.y_values_send_envlope = [0 for i in range(arrlen)]
        self.thread = Thread(target = self.threaded_function, args = (1, ))
        self.thread.start()
        self.listeners = []

    '''
    After 3 seconds this thread initializes the arduino communication.
    After that it recieves the Arduino Data and writes it to the y_values_... arrays
    '''
    def threaded_function(self, arg) -> None:
        def write_valueLst_to_arrays(lst) ->None:
            if(len(lst) == 4):
                self.x_queue.pop(0)
                self.x_queue.append(lst[3])
                self.y_values_send_raw_data.pop(0)
                self.y_values_send_raw_data.append(lst[0])
                self.y_values_send_filtered_data.pop(0)
                self.y_values_send_filtered_data.append(lst[1])
                self.y_values_send_envlope.pop(0)
                self.y_values_send_envlope.append(lst[2])
            # else:
            #     print("bad values:")
            #     print(lst)
        
        time.sleep(3)
        PDRG.PiDataReceiverGeneric.init_arduino(self)
        lst = PDRG.PiDataReceiverGeneric.read(self)
        if(len(lst) == 4):
            write_valueLst_to_arrays(lst)

        while 1:
            lst = PDRG.PiDataReceiverGeneric.read(self)
            write_valueLst_to_arrays(lst)
            
            for func in self.listeners:
                func(lst)
            
    
    """
    calles the given function, when new data is recieved
    the function will recieve one parameter, which is a list with the data
    """
    def connect_new_data_event(self, connect_func) -> None:
        self.listeners.append(connect_func)

    """
    disconnects the previously connected function
    """
    def disconnect_new_data_event(self, connect_func) -> None:
        if self.listeners.count(connect_func) > 0:
            self.listeners.remove(connect_func)
