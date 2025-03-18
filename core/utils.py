from PyQt5 import QtWidgets, QtCore

class WaypointDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un waypoint")
        
        layout = QtWidgets.QFormLayout(self)
        
        self.latitude = QtWidgets.QLineEdit()
        self.longitude = QtWidgets.QLineEdit()
        self.altitude = QtWidgets.QSpinBox()
        self.altitude.setRange(1, 100)
        
        layout.addRow("Latitude :", self.latitude)
        layout.addRow("Longitude :", self.longitude)
        layout.addRow("Altitude (m) :", self.altitude)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)