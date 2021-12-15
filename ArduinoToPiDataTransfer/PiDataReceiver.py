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
    '''
    def __init__(self, port, threshold) -> None:
        
        super().__init__(port, threshold=threshold, baudrate=115200, timeout=.1, send_raw_data = True, send_filtered_data = True, send_envlope = True, data_separation=",")
        # 10000 values should store roughly 5 seconds
        arrlen = 10000
        # fill with zeros, so the displayed Graph does not change in length while it fills
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
        # need to wait 3 seconds here, to wait for arduino connection to set-up
        time.sleep(3)
        PDRG.PiDataReceiverGeneric.init_arduino(self)
        
        while 1:
            lst = PDRG.PiDataReceiverGeneric.read(self)

            if(len(lst) == 4):
                self.y_values_send_raw_data.pop(0)
                self.y_values_send_raw_data.append(lst[0])
                self.y_values_send_filtered_data.pop(0)
                self.y_values_send_filtered_data.append(lst[1])
                self.y_values_send_envlope.pop(0)
                self.y_values_send_envlope.append(lst[2])
                self.x_queue.pop(0)
                # /1000000 converts the nanoseconds to seconds
                self.x_queue.append(lst[3]/1000000)
            
            # signal data-listeners
            for func in self.listeners:
                func(lst)
            
    
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
