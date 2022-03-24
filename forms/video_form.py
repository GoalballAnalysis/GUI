# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/mebas/Documents/untitled/form.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QToolButton


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, parent):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        ##################################
        self.inputFileLineEdit = QLineEdit(self.centralwidget)
        self.inputFileLineEdit.setPlaceholderText("Video yolunu seçiniz.") 
        self.inputFileLineEdit.setGeometry(QtCore.QRect(30, 10, 285, 32))
        self.inputFileLineEdit.setText(MainWindow.videoPath)
        self.inputFileLineEdit.textChanged.connect(self.editPath)

        self.inputFileButton = QToolButton(self.centralwidget)
        self.inputFileButton.setGeometry(QtCore.QRect(280, 12, 33, 28))
        self.inputFileButton.setText("...")
        self.inputFileButton.clicked.connect(lambda: self.browseHandler(MainWindow))

        self.forwardButton =  QtWidgets.QPushButton(self.centralwidget)
        self.forwardButton.setGeometry(QtCore.QRect(320, 9, 80, 34))
        self.forwardButton.setText("Open Video")
        self.forwardButton.clicked.connect(lambda: MainWindow.startVideoWorker())
        ##################################
        self.rewindButton = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton.setGeometry(QtCore.QRect(1240, 550, 80, 24))
        self.rewindButton.setObjectName("pushButton_2")

        self.fastForwardButton = QtWidgets.QPushButton(self.centralwidget)
        self.fastForwardButton.setGeometry(QtCore.QRect(1321, 550, 80, 24))
        self.fastForwardButton.setObjectName("pushButton_3")
        
        self.startStopButton = QtWidgets.QPushButton(self.centralwidget)
        self.startStopButton.setGeometry(QtCore.QRect(1240, 580, 160, 24))
        self.startStopButton.setObjectName("pushButton")

        self.forwardToStats = QtWidgets.QPushButton(self.centralwidget)
        self.forwardToStats.setGeometry(QtCore.QRect(1240, 10, 160, 24))
        self.forwardToStats.setObjectName("pushButton")

        self.checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkbox.setGeometry(QtCore.QRect(1240, 480, 160, 24))
        self.checkbox.setChecked(True)

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 60, 1200, 840))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.startStopButton.clicked.connect(MainWindow.StopFeed)
        self.rewindButton.clicked.connect(MainWindow.Backward)
        self.fastForwardButton.clicked.connect(MainWindow.Forward)
        self.forwardToStats.clicked.connect(lambda: self.goToStats(parent,2))
        self.checkbox.stateChanged.connect(MainWindow.TrackState)

    def browseHandler(self, parent):
        self.open_dialog_box(parent)
        
    def open_dialog_box(self, parent):
        filename = QFileDialog.getOpenFileName()
        self.path = filename[0]
        parent.videoPath = self.path
        self.inputFileLineEdit.setText(self.path)
    
    def editPath(self,text): 
        self.path = text

    def goToStats(self, parent, index):
        parent.changeTab(index)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.rewindButton.setText(_translate("MainWindow", "Geri"))
        self.fastForwardButton.setText(_translate("MainWindow", "İleri"))
        self.startStopButton.setText(_translate("MainWindow", "Başlat/Durdur"))
        self.forwardToStats.setText(_translate("MainWindow", "İstatistik Ekranına Devam Et"))
        self.checkbox.setText(_translate("MainWindow", "Tracking"))

