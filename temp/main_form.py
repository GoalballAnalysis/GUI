
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        

        self.buttons = QtWidgets.QVBoxLayout()

        self.but = QtWidgets.QPushButton("ALALALAL")
        self.buttons.addWidget(self.but)

        self.centralwidget.setLayout(self.buttons)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1700, 890, 80, 24))
        self.pushButton.setObjectName("pushButton")

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(1700, 840, 80, 24))
        self.pushButton_2.setObjectName("pushButton_2")
    
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(1700, 790, 80, 24))
        self.pushButton_3.setObjectName("pushButton_3")
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(MainWindow.StopFeed)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Başlat/Durdur"))
        self.pushButton_2.setText(_translate("MainWindow", "Geri"))
        self.pushButton_3.setText(_translate("MainWindow", "İleri"))

