from PyQt5 import QtCore, QtWidgets

class KeyInputLineEdit(QtWidgets.QLineEdit):
    keyPressed = QtCore.pyqtSignal(str)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        
        # Gestion des touches spéciales
        if key == QtCore.Qt.Key_Space:
            self.setText("SPACE")
            self.keyPressed.emit("SPACE")
        elif modifiers == QtCore.Qt.ControlModifier:
            self.setText("CTRL")
            self.keyPressed.emit("CTRL")
        else:
            text = event.text().upper()
            if text:
                self.setText(text)
                self.keyPressed.emit(text)
        event.accept()