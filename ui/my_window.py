from PyQt5 import QtWidgets, QtGui, QtCore
from main_window import Ui_MainWindow
import sys
import os, json

# Obtenir le chemin absolu du répertoire parent
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.video_thread import VideoThread
from core.serial_thread import SerialThread
from config.settings import SettingsDialog

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
        
        # Initialisation pour le menu
        self.sidebar_width = self.sideBar.width()
        self.menu_visible = True
        
        # Initialisation pour le flux vidéo
        # Références aux QLabels
        self.video_manual = self.findChild(QtWidgets.QLabel, "videoFeed")
        self.video_auto = self.findChild(QtWidgets.QLabel, "videoFeedAuto")
        # Initialiser les labels FPS
        self.fps_label_manual = self.findChild(QtWidgets.QLabel, "fpsLabelManual")
        self.fps_label_auto = self.findChild(QtWidgets.QLabel, "fpsLabelAuto")

        # Initialisation vidéo
        self.init_video()
        self.video_thread.error_signal.connect(self.handle_video_error)
        # Connecter le signal FPS
        self.video_thread.fps_signal.connect(self.update_fps)

        # Initialisation pour les données en série
        self.init_serial()

        # Initialisation pour les settings
        self.touchConfig.clicked.connect(self.configure_keys)

    # Fonction liée au menu
    def toggle_menu(self):
        icon1 = QtGui.QIcon()
        if self.menu_visible:
            icon1.addPixmap(QtGui.QPixmap( str(ressources_path) + "/toggleMenuClosed.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon1.addPixmap(QtGui.QPixmap( str(ressources_path) + "/toggleMenuOpened.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toggleBtn.setIcon(icon1)
        self.menu_visible = not self.menu_visible
        self.sideBar.setFixedWidth(self.sidebar_width if self.menu_visible else 0)

    # Fonctions liées au flux vidéo
    def init_video(self):
        # Créer le thread vidéo
        self.video_thread = VideoThread(src=0)  # src='udp://@0.0.0.0:11111' pour le port par défaut, src=0 pour la webcam et src=1 si je branche une seconde webcam
        self.video_thread.change_pixmap.connect(self.update_video_feeds)
        self.video_thread.start()
        
    def update_video_feeds(self, image, mode):
        # Stocker les dernières images
        if mode == 'manual':
            self.current_manual_image = image
            label = self.videoFeed
        elif mode == 'auto':
            self.current_auto_image = image
            label = self.videoFeedAuto
        
        # Mise à jour du QLabel
        if label.isVisible():  # Ne mettre à jour que si le mode est actif
            pixmap = QtGui.QPixmap.fromImage(image).scaled(
                label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            label.setPixmap(pixmap)

    def resizeEvent(self, event):
        # Redimensionner uniquement les pixmaps existants
        if hasattr(self, 'current_manual_image'):
            self.update_video_feeds(self.current_manual_image, 'manual')
        if hasattr(self, 'current_auto_image'):
            self.update_video_feeds(self.current_auto_image, 'auto')
        super().resizeEvent(event)
    def closeEvent(self, event):
        """S'assurer que le thread vidéo est bien arrêté"""
        self.video_thread.stop()
        self.video_thread.wait()
        event.accept()
    def handle_video_error(self, message):
        """Afficher les erreurs dans les logs"""
        self.logViewer.addItem(f"ERREUR VIDÉO: {message}")
        self.video_thread.stop()
    def update_fps(self, fps):
        """Met à jour l'affichage du FPS pour les deux modes"""
        text = f"FPS: {fps:.1f}"
        self.fps_label_manual.setText(text)
        self.fps_label_auto.setText(text)

    # Fonctions liées au données en série
    def init_serial(self):
        """Initialise la connexion série avec le récepteur ELRS"""
        try:
            # Adapter le port selon le système (COM3, /dev/ttyUSB0, etc.)
            self.serial_thread = SerialThread(port='COM3', baudrate=115200)
            self.serial_thread.data_received.connect(self.update_telemetry)
            self.serial_thread.error_signal.connect(self.handle_serial_error)
            self.serial_thread.start()
            
        except Exception as e:
            self.logViewer.addItem(f"ERREUR SÉRIE: {str(e)}")
    def update_telemetry(self, data):
        """Met à jour les données télémétriques dans les deux modes"""
        try:
            # Formater les données (exemple de format: "ALT:100m;SPD:30km/h;SAT:12")
            formatted_data = self.parse_telemetry(data)
            
            self.teleViewer.setPlainText(formatted_data)
            self.teleViewerAuto.setPlainText(formatted_data)
            
        except Exception as e:
            self.logViewer.addItem(f"ERREUR TÉLÉMÉTRIE: {str(e)}")
    def parse_telemetry(self, raw_data):
        """Convertit les données brutes en format lisible"""
        # Adapter selon le format du récepteur
        parts = raw_data.split(';')
        formatted = ""
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                formatted += f"{key.strip()}: {value.strip()}\n"
        return formatted or "Aucune donnée reçue"
    def handle_serial_error(self, message):
        self.logViewer.addItem(f"ERREUR: {message}")
        self.serial_thread.stop()
    def closeEvent(self, event):
        # Ajouter la fermeture série
        self.serial_thread.stop()
        self.video_thread.stop()
        event.accept()

    # Fonctions liées aux touches
    def load_key_bindings(self):
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

    def configure_keys(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            self.key_bindings = dialog.get_current_keys()

    def keyPressEvent(self, event):
        key = None
        if event.key() == QtCore.Qt.Key_Space:
            key = "SPACE"
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            key = "CTRL"
        else:
            key = event.text().upper()

        command = None
        if key == self.key_bindings.get('takeoff'):
            command = "TAKEOFF"
        elif key == self.key_bindings.get('land'):
            command = "LAND"
        elif key == self.key_bindings.get('forward'):
            command = "FORWARD"
        elif key == self.key_bindings.get('backward'):
            command = "BACKWARD"
        elif key == self.key_bindings.get('right'):
            command = "RIGHT"
        elif key == self.key_bindings.get('left'):
            command = "LEFT"

        if command:
            self.serial_thread.send(command)

app = QtWidgets.QApplication(sys.argv)

# Chemin relatif au fichier Python
css_path = os.path.join(os.path.dirname(__file__), 'style.css')
with open(css_path, 'r') as f:
    app.setStyleSheet(f.read())

window = myWindow()
window.show()

sys.exit(app.exec())