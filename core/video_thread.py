import cv2
from PyQt5 import QtCore, QtGui
import time 

class VideoThread(QtCore.QThread):
    change_pixmap = QtCore.pyqtSignal(QtGui.QImage, str)
    error_signal = QtCore.pyqtSignal(str)  # Nouveau signal d'erreur
    fps_signal = QtCore.pyqtSignal(float)  # Nouveau signal pour le FPS

    def __init__(self, src=0):
        super().__init__()
        self.src = src
        self.running = True
        self.frame_delay = 30  # ms (≈33 FPS)
        self.frame_count = 0
        self.start_time = None

    def run(self):
        try:
            cap = cv2.VideoCapture(self.src)
            if not cap.isOpened():
                self.error_signal.emit(f"Impossible d'ouvrir le flux {self.src}")
                return

            while self.running:
                start = time.time()
                ret, frame = cap.read()
                if not ret:
                    self.error_signal.emit("Erreur de lecture du flux vidéo")
                    break
                
                # Calcul du FPS
                if self.frame_count % 10 == 0:  # Mettre à jour toutes les 10 frames
                    if self.start_time is None:
                        self.start_time = time.time()
                    else:
                        elapsed = time.time() - self.start_time
                        fps = self.frame_count / elapsed
                        self.fps_signal.emit(fps)
                        self.frame_count = 0
                        self.start_time = time.time()

                # Traitement de l'image
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                
                self.frame_count += 1

                # Émettre seulement si nécessaire
                if self.running:  # Vérification supplémentaire
                    self.change_pixmap.emit(qt_image, 'manual')
                    self.change_pixmap.emit(qt_image, 'auto')

                # Limiter le taux de rafraîchissement
                QtCore.QThread.msleep(self.frame_delay)

        except Exception as e:
            self.error_signal.emit(f"Erreur critique: {str(e)}")
        finally:
            cap.release()

    def stop(self):
        self.running = False
        self.wait()