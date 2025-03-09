from PyQt5 import QtWidgets, QtGui
from main_window import Ui_MainWindow
import sys
import os

from pathlib import Path

# Chemin absolu vers l'icône
ressources_path = Path(__file__).parent.parent / "ressources"

# Si 1ère fois que main_window est import depuis Qt Designer, il faut :
# - Changer le chemin de l'icone de l'app comme ceci
"""
from pathlib import Path

# Chemin absolu vers l'icône
ressources_path = Path(__file__).parent.parent / "ressources"

icon.addPixmap(QtGui.QPixmap(str(ressources_path) + "/AppIcon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
"""

class myWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(myWindow, self).__init__()
        self.setupUi(self)

        # Connexions
        self.toggleBtn.clicked.connect(self.toggle_menu)
        self.manualMode.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.autoMode.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        
        # Initialisation
        self.sidebar_width = 200
        self.menu_visible = True

    def toggle_menu(self):
        icon1 = QtGui.QIcon()
        if self.menu_visible:
            icon1.addPixmap(QtGui.QPixmap( str(ressources_path) + "/toggleMenuClosed.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon1.addPixmap(QtGui.QPixmap( str(ressources_path) + "/toggleMenuOpened.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toggleBtn.setIcon(icon1)
        self.menu_visible = not self.menu_visible
        self.sideBar.setFixedWidth(self.sidebar_width if self.menu_visible else 0)

app = QtWidgets.QApplication(sys.argv)

# Chemin relatif au fichier Python
css_path = os.path.join(os.path.dirname(__file__), 'style.css')
with open(css_path, 'r') as f:
    app.setStyleSheet(f.read())

window = myWindow()
window.show()

sys.exit(app.exec())