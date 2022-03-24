

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StatisticWindow(object):
    def setupUi(self, IntroWindow):
        # IntroWindow.setObjectName("IntroWindow")
        # IntroWindow.resize(1500, 1000)
        # self.centralwidget = QtWidgets.QWidget(IntroWindow)
        # self.centralwidget.setObjectName("centralwidget")

        self.layout = QtWidgets.QVBoxLayout(IntroWindow)
        self.button1 =  QtWidgets.QPushButton("İstatistik Ekranı")
        self.button1.setGeometry(QtCore.QRect(80, 130, 113, 32))
        self.layout.addWidget(self.button1)
        
        IntroWindow.setLayout(self.layout)

        # self.pushButton = QtWidgets.QPushButton("BASS")
        # self.pushButton.setGeometry(QtCore.QRect(1240, 580, 160, 24))
        # self.pushButton.setObjectName("pushButton")

    #     self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
    #     self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 60, 1200, 840))
    #     self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

    #     self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
    #     self.verticalLayout.setContentsMargins(0, 0, 0, 0)
    #     self.verticalLayout.setObjectName("verticalLayout")
        
    #     IntroWindow.setCentralWidget(self.centralwidget)

    #     self.retranslateUi(IntroWindow)
    #     QtCore.QMetaObject.connectSlotsByName(IntroWindow)

    # def retranslateUi(self, IntroWindow):
    #     _translate = QtCore.QCoreApplication.translate
    #     IntroWindow.setWindowTitle(_translate("IntroWindow", "IntroWindow"))
    #     self.pushButton.setText(_translate("IntroWindow", "BASS"))
        

