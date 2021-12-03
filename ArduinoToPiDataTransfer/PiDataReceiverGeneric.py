import serial
import serial.tools.list_ports

class PiDataReceiverGeneric:
    '''
    port must be a string like 'COM3'. Retrieve possible ports with PiDataReceiver.list_possible_ports
    '''
    def __init__(self, port, baudrate=115200, timeout=.1, send_raw_data = False, send_filtered_data = False, send_envlope = True, data_separation=",") -> None:
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.send_raw_data = send_raw_data
        self.send_filtered_data = send_filtered_data
        self.send_envlope = send_envlope
        self.data_separation = data_separation

    '''
    wait a bit to call this function after PiDataReceiver was initiated. 2Seconds is good
    '''
    def init_arduino(self):
        self.clear_arduino_buffer()
        
        d = self.data_separation

        if(self.send_raw_data):
            d += "1"
        else:
            d += "0"

        if(self.send_filtered_data):
            d += "1"
        else:
            d += "0"
        
        if(self.send_envlope):
            d += "1"
        else:
            d += "0"

        self.write(d)

    def write(self, x):
        self.arduino.write(bytes(x, 'utf-8'))
        return

    '''
    reads last line that arduino send
    returns list of int. 
    List may contain raw_data, filtered_data, envlope, depending on send_raw_data and the other attributes.
    The last value is a Timestamp of the moment when the analoge value was read
    '''
    def read(self):
        try:
            # data = self.arduino.read(self.arduino.in_waiting)
            data = self.arduino.readline()
            data = data.decode('utf-8')
            # data = data.split('\r\n')
            # data = data.pop()
            data = data.split(self.data_separation)
            data = list(map(int, data)) #convert strings to int
            
        except:
            data = []
        return data

    '''
        should be called before you start to read or write values for the first time after a connect, in case there are still old values in the buffer
    '''
    def clear_arduino_buffer(self) -> None:
        self.arduino.reset_input_buffer()
        self.arduino.reset_output_buffer()
        pass
    '''
    staticmethod
    returns list with items like this: 
    ('COM3', 'Arduino Due Programming Port (COM3)', 'USB VID:PID=2341:003D SNR=75330303035351300230')
    '''
    @staticmethod
    def list_possible_ports():
        return list(serial.tools.list_ports.comports())