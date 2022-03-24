import os
from pathlib import Path
from shutil import which
import sys
from threading import Thread
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtWidgets, QtCore
import numpy as np
from form_python import Ui_MainWindow
import DrawLines.drawlines as drawlines
from time import sleep

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.showMaximized()
        self.VBL = QtWidgets.QVBoxLayout()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.FeedLabel = QLabel()
        # self.FeedLabel.setStyleSheet("background-color: yellow;")
        self.VBL.addWidget(self.FeedLabel)


        self.ui.centralwidget.setLayout(self.VBL)

        # self.Worker1 = Worker1()
        # self.Worker1.start()
        # self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        
    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def StopFeed(self):
        self.Worker1.stop()



class Worker1(QThread):
    def __init__(self):
        super().__init__()
        self.cap = drawlines.open_video('video.mp4')
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        
        while self.ThreadActive:
            sleep(0.015)
            ret, frame = drawlines.main(self.cap)
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1000, 700, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
    def stop(self):
        self.ThreadActive = not self.ThreadActive
        if self.ThreadActive:
            self.start()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
