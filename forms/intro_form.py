

from importlib.resources import path
from unittest.mock import patch
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QToolButton
from PyQt5.QtGui import *

class Ui_IntroWindow(object):
    def setupUi(self, IntroWindow, parent):
        self.path = None
        self.inputFileButton = QToolButton(IntroWindow)
        self.inputFileButton.setGeometry(QtCore.QRect(1280, 830, 40, 30))
        self.inputFileButton.setText("...")
        self.inputFileButton.clicked.connect(lambda: self.browseHandler(IntroWindow))

        self.inputFileLineEdit = QLineEdit(IntroWindow)
        self.inputFileLineEdit.setPlaceholderText("Video yolunu seçiniz.") 
        self.inputFileLineEdit.setGeometry(QtCore.QRect(1030, 831, 250, 28))
        self.inputFileLineEdit.setText(self.path)
        self.inputFileLineEdit.textChanged.connect(self.editPath)

        self.forwardButton =  QtWidgets.QPushButton(IntroWindow)
        self.forwardButton.setGeometry(QtCore.QRect(1030, 900, 250, 28))
        self.forwardButton.setText("İleri")
        self.forwardButton.clicked.connect(lambda: self.sendPath(parent,1))

    def sendPath(self, parent, index):
        parent.transferPath()
        parent.changeTab(index)
        # parent.tabs.setCurrentIndex(index)

    def editPath(self,text): 
        self.path = text

    def browseHandler(self, parent):
        self.open_dialog_box(parent)
        
    def open_dialog_box(self, parent):
        filename = QFileDialog.getOpenFileName()
        self.path = filename[0]
        parent.path = self.path
        self.inputFileLineEdit.setText(self.path)

    def testFunc(self): 
        print(self.path)

        

