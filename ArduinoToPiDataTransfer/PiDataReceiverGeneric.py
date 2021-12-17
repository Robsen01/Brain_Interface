from time import sleep, time_ns
import serial
import serial.tools.list_ports

'''
PiDataReceiverGeneric is a very universal class, which has everything you need to communicate with the Arduino.
'''
class PiDataReceiverGeneric:

    '''
    port must be a string like 'COM3'. Retrieve possible ports with PiDataReceiver.list_possible_ports.
    '''
    def __init__(self, port, threshold, baudrate=115200, timeout=.1, send_raw_data=False, send_filtered_data=False, send_envlope=True, data_separation=",") -> None:
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.send_raw_data = send_raw_data
        self.send_filtered_data = send_filtered_data
        self.send_envlope = send_envlope
        self.data_separation = data_separation
        self.threshold = threshold

    '''
    Closes the potentialy open port to the arduino that may be connected.
    Should be called, before disposing this object
    '''
    def close_arduino_port(self):
        if hasattr(self, "arduino"):
            if not self.arduino.closed:
                self.arduino.close()

    '''
    Wait a bit to call this function after PiDataReceiver was initiated. 2-3 Seconds is good.
    This sends a string to the Arduino to configure it.
    Returns true, if the Arduino responded that all is well.
    '''
    def init_arduino(self) -> bool:
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
        
        if(self.threshold and type(self.threshold) == int and self.threshold > 0):
            d += str(self.threshold)
        else:
            d+= "0"

        self.write(d)
        self.arduino.flushOutput()

        # wait till response, there will be some empty lines before the response. The loop reads them out, until the response arrives
        time = time_ns()
        data = ""
        while data != "all good":
            print(time_ns() - time)
            print("\n")
            data = self.arduino.readline()
            data = data.decode('utf-8')
            data = data.strip()
            print(time_ns() - time)
            print("\n" + data)
            # wait max 1.5 s for response (takes almost exactly 1s on my machine)
            if time_ns() - time > 1500000000:
                break

        
        if data == "all good":
            return True
        
        return False

    '''
    This function writes a string to the Arduino.
    '''
    def write(self, s) -> None:
        self.arduino.write(bytes(s, 'utf-8'))

    '''
    Reads last line that arduino send.
    Returns list of int. 
    List may contain raw_data, filtered_data, envlope, depending on send_raw_data and the other attributes.
    The last value is a Timestamp of the moment when the analoge value was read.
    '''
    def read(self):
        try:
            data = self.arduino.readline()
            data = data.decode('utf-8')
            data = data.split(self.data_separation)
            data = list(map(int, data))  # convert strings-list to int-list
        except:
            # when getting started Arduino sends some setup lines. This helps to ignore them
            data = []
        return data

    '''
    Should be called before you start to read or write values for the first time after a connect, in case there are still old values in the buffer.
    '''
    def clear_arduino_buffer(self) -> None:
        self.arduino.reset_input_buffer()
        self.arduino.reset_output_buffer()

    '''
    staticmethod
    Returns list with items like this: 
    ('COM3', 'Arduino Due Programming Port (COM3)', 'USB VID:PID=2341:003D SNR=75330303035351300230')
    The first String in this list that represents the Arduino must be used for the port-parameter of PiDataReceiverGeneric
    '''
    @staticmethod
    def list_possible_ports():
        return list(serial.tools.list_ports.comports())
