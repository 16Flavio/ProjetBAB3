import serial
from PyQt5 import QtCore, QtWidgets

class SerialThread(QtCore.QThread):
    data_received = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            
            while self.running and self.ser.is_open:
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    self.data_received.emit(data)

        except Exception as e:
            self.error_signal.emit(f"Erreur série: {str(e)}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.wait()