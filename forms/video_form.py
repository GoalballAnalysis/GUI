# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/mebas/Documents/untitled/form.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from tkinter import E
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QToolButton


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, parent):
        self.selected_mode = ""
        self.parent = parent
        self.mode_selected = False
        ################################
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
        self.forwardButton.clicked.connect(lambda: MainWindow.openVideo())


        #############################checkboxes for mode selection
        self.radiobutton1 = QtWidgets.QRadioButton(self.centralwidget)
        # self.radiobutton.setChecked(True)
        self.radiobutton1.setText("Mode 1")
        self.radiobutton1.mode = "Mode 1"
        self.radiobutton1.setGeometry(QtCore.QRect(900, 9, 150, 34))
        self.radiobutton1.toggled.connect(self.modeSelection)

        self.radiobutton2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radiobutton2.setText("Mode 2")
        self.radiobutton2.mode = "Mode 2"
        self.radiobutton2.setGeometry(QtCore.QRect(1000, 9, 150, 34))
        self.radiobutton2.toggled.connect(self.modeSelection)

        self.radiobutton3 = QtWidgets.QRadioButton(self.centralwidget)
        self.radiobutton3.setText("Mode 3")
        self.radiobutton3.mode = "Mode 3"
        self.radiobutton3.setGeometry(QtCore.QRect(1100, 9, 150, 34))
        self.radiobutton3.toggled.connect(self.modeSelection)

        self.radiobutton4 = QtWidgets.QRadioButton(self.centralwidget)
        self.radiobutton4.setText("Mode 4")
        self.radiobutton4.mode = "Mode 4"
        self.radiobutton4.setGeometry(QtCore.QRect(1200, 9, 150, 34))
        self.radiobutton4.toggled.connect(self.modeSelection)

        # self.mode1_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        # self.mode1_checkbox.setGeometry(QtCore.QRect(900, 9, 150, 34))
        # self.mode1_checkbox.setText("Mode 1")

        # display stats
        self.logStats = QtWidgets.QTextEdit(self.centralwidget)
        self.logStats.setReadOnly(True)
        self.logStats.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        self.sb = self.logStats.verticalScrollBar()
        self.sb.setValue(self.sb.maximum())
        self.logStats.append(self.selected_mode)
        self.logStats.setGeometry(1340, 210, 400, 250)
        #############################

        # label when a goal is detected 
        self.goal_label = QtWidgets.QLabel(self.centralwidget)
        self.goal_label.setText("GOOOOL")
        self.goal_label.setGeometry(1340, 110, 160, 24)
        self.goal_label.hide()

        # One Person Tracking Button
        self.onePersonTrack =  QtWidgets.QPushButton(self.centralwidget)
        self.onePersonTrack.setGeometry(QtCore.QRect(500, 9, 150, 34))
        self.onePersonTrack.setText("One Person Track")
        self.onePersonTrack.setObjectName("onePersonTrack")
        self.onePersonTrack.clicked.connect(lambda: MainWindow.onePersonTrack())

        # one person tracking reset
        self.resetOnePersonTrack =  QtWidgets.QPushButton(self.centralwidget)
        self.resetOnePersonTrack.setGeometry(QtCore.QRect(700, 9, 150, 34))
        self.resetOnePersonTrack.setText("Reset One Person Track")
        self.resetOnePersonTrack.setObjectName("resetOnePersonTrack")
        self.resetOnePersonTrack.setEnabled(False)
        self.resetOnePersonTrack.clicked.connect(lambda: MainWindow.resetOnePersonTrack())

        ##################################
        self.startStopButton = QtWidgets.QPushButton(self.centralwidget)
        self.startStopButton.setGeometry(QtCore.QRect(10, 800, 160, 24))
        self.startStopButton.setObjectName("pushButton")

        self.rewindButton = QtWidgets.QPushButton(self.centralwidget)
        self.rewindButton.setGeometry(QtCore.QRect(210, 800, 80, 24))
        self.rewindButton.setObjectName("pushButton_2")

        self.fastForwardButton = QtWidgets.QPushButton(self.centralwidget)
        self.fastForwardButton.setGeometry(QtCore.QRect(291, 800, 80, 24))
        self.fastForwardButton.setObjectName("pushButton_3")
    
        self.checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkbox.setGeometry(QtCore.QRect(410, 800, 160, 24))
        self.checkbox.setChecked(True)
        
        self.forwardToStats = QtWidgets.QPushButton(self.centralwidget)
        self.forwardToStats.setGeometry(QtCore.QRect(1390, 10, 160, 24))
        self.forwardToStats.setObjectName("pushButton")

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

    def modeSelection(self):
        radioButton = self.parent.sender()
        if self.mode_selected is False and radioButton.isChecked():
            print("Mode is %s" % (radioButton.mode))
            self.selected_mode = radioButton.mode
            self.mode_selected = True
            for rb in self.parent.findChildren(QtWidgets.QRadioButton):
                if rb is not radioButton:
                    rb.setDisabled(True)
            title = "Displaying " + radioButton.mode +" Stats"
            self.logStats.append(title)
            self.logStats.append("-"*(len(title)+5))

   
    def browseHandler(self, parent):
        self.open_dialog_box(parent)
        
    def open_dialog_box(self, parent):
        filename = QFileDialog.getOpenFileName()
        self.path = filename[0]
        parent.videoPath = self.path
        self.inputFileLineEdit.setText(self.path)

    def changeGoalVisibilty(self):
        if self.goal_label.isVisible():
            self.goal_label.hide()
        else:
            self.goal_label.show()
    
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

