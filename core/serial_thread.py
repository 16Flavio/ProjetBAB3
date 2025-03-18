import serial
from PyQt5 import QtCore, QtWidgets

class SerialThread(QtCore.QThread):
    data_received = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    command_queue = QtCore.pyqtSignal(str)

    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.ser = None
        self.commands = []  # Liste des commandes à envoyer

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
            
            while self.running:
                # Envoyer les commandes de la file d'attente
                if self.commands:
                    cmd = self.commands.pop(0)
                    try:
                        self.ser.write(f"{cmd}\n".encode())
                    except Exception as e:
                        self.error_signal.emit(f"Erreur envoi: {str(e)}")
                
                # Lire les données (non bloquant)
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    self.data_received.emit(data)
                
                QtCore.QThread.msleep(10)  # Réduire la charge CPU

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
    def send(self, command):
        """Ajoute une commande en tête de file si urgente"""
        if command in ["STOP_AUTO", "LAND"]:
            self.commands.insert(0, command)  # Priorité haute
        else:
            self.commands.append(command)