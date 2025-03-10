import json
from PyQt5 import QtWidgets, QtCore, QtGui
import sys, os
from PyQt5.uic import loadUi

# Obtenir le chemin absolu du répertoire parent
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from ui.settings_dialog import Ui_Settings

class SettingsDialog(QtWidgets.QDialog, Ui_Settings):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.keys = self.load_keys()
        self.setup_inputs()
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)
    def on_accept(self):
        """Sauvegarde les touches et ferme la fenêtre"""
        self.save_keys()
        self.accept()  # Ferme la fenêtre avec le statut "Accepted"
    def setup_inputs(self):
        inputs = {
            'takeoff': self.takeoffInput,
            'land': self.landInput,
            'forward': self.forwardInput,
            'backward': self.backwardInput,
            'right': self.rightInput,
            'left': self.leftInput
        }
        
        for key, widget in inputs.items():
            widget.setText(self.keys.get(key, ""))
            widget.setReadOnly(True)
            widget.mousePressEvent = lambda event, w=widget: self.start_capture(w)

    def start_capture(self, widget):
        widget.grabKeyboard()
        widget.clear()

    def get_current_keys(self):
        return {
            'takeoff': self.takeoffInput.text(),
            'land': self.landInput.text(),
            'forward': self.forwardInput.text(),
            'backward': self.backwardInput.text(),
            'right': self.rightInput.text(),
            'left': self.leftInput.text()
        }

    def load_keys(self):
        try:
            with open('key_bindings.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'takeoff': 'T',
                'land': 'L',
                'forward': 'Z',
                'backward': 'S',
                'right': 'D',
                'left': 'Q'
            }

    def save_keys(self):
        new_keys = self.get_current_keys()
        if len(set(new_keys.values())) != len(new_keys):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Touches en conflit !")
            return

        with open('key_bindings.json', 'w') as f:
            json.dump(new_keys, f, indent=4)