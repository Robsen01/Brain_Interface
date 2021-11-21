import serial

class GraphVisualizer:
    '''
    port must be a string like 'COM3'. Retrieve possible ports with GraphVisualizer.list_possible_ports
    '''
    def __init__(self, port, baudrate=115200, timeout=.1) -> None:
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def write_read(self, x):
        self.arduino.write(bytes(x, 'utf-8'))
        return

    def read(self):
        data = self.arduino.readline()
        return data

    '''
        staticmethod
        returns list with items like this: 
        ('COM4', 'Arduino Due Programming Port (COM4)', 'USB VID:PID=2341:003D SNR=75330303035351300230')
    '''
    @staticmethod
    def list_possible_ports():
        return list(serial.tools.list_ports.comports())