import sys
sys.path.append('../Brain_Interface')
import ArduinoToPiDataTransfer.PiDataReceiverGeneric as PDRG
from threading import Thread
import time

class PiDataReceiver(PDRG.PiDataReceiverGeneric):
    '''
    port must be a string like 'COM3'. Retrieve possible ports with PiDataReceiver.list_possible_ports
    Also initializes the arduino communication. 
    Also starts a thread that reads y
    '''
    def __init__(self, port) -> None:
        
        super().__init__(port, baudrate=115200, timeout=.1, send_raw_data = True, send_filtered_data = True, send_envlope = True, data_separation=",")
        # 10000 values should store the 10 seconds
        self.x_queue = [0 for i in range(10000)]
        self.y_values_send_raw_data = [0 for i in range(10000)]
        self.y_values_send_filtered_data = [0 for i in range(10000)]
        self.y_values_send_envlope = [0 for i in range(10000)]
        self.thread = Thread(target = self.threaded_function, args = (1, ))
        self.thread.start()

    '''
    After 3 seconds this thread initializes the arduino communication.
    After that it recieves the Arduino Data and writes it to the y_values_... arrays
    '''
    def threaded_function(self, arg) -> None:

        time.sleep(3)
        PDRG.PiDataReceiverGeneric.init_arduino(self)
        tt_start = time.thread_time()
        lst = PDRG.PiDataReceiverGeneric.read(self)

        if(len(lst) == 3):
            self.x_queue.pop()
            self.x_queue.insert(0, 0)
            self.y_values_send_raw_data.pop()
            self.y_values_send_raw_data.insert(0, lst[0])
            self.y_values_send_filtered_data.pop()
            self.y_values_send_filtered_data.insert(0, lst[1])
            self.y_values_send_envlope.pop()
            self.y_values_send_envlope.insert(0, lst[2])
        # else:
        #     print("bad values:")
        #     print(lst)

        while 1:
            lst = PDRG.PiDataReceiverGeneric.read(self)

            if(len(lst) == 3):
                self.x_queue.pop()
                self.x_queue.insert(0, time.thread_time() - tt_start)
                self.y_values_send_raw_data.pop()
                self.y_values_send_raw_data.insert(0, lst[0])
                self.y_values_send_filtered_data.pop()
                self.y_values_send_filtered_data.insert(0, lst[1])
                self.y_values_send_envlope.pop()
                self.y_values_send_envlope.insert(0, lst[2])
            # else:
            #     print("bad values:")
            #     print(lst)