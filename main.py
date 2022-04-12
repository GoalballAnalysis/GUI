
from random import random
from shutil import which
import sys
import os
from tabnanny import check
from tkinter import N

from matplotlib.pyplot import xlim
sys.path.append(os.path.join("tracker","yolov5"))
sys.path.append(os.path.join("tracker","deepsort"))
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtCore
from forms.video_form import Ui_MainWindow
from forms.intro_form import Ui_IntroWindow
from forms.wrapper_form import Ui_WrapperWindow
from forms.stats_form  import Ui_StatisticWindow
from workers.worker1 import Worker1
from PyQt5 import QtGui
import cv2
from time import sleep


#ToDo
# Butonların çalışması da video seçilmişte gerçekleştirilecek, aksi takdirde disabled durumda olacaklar.yapıldı
#


# reverse of image size
IMAGE_SIZE = (1280, 720)
GIF_SIZE = (150,150)

class OnePersonTracker:
    def __init__(self):
        """
        # selected person id
        self.id=None
        """

        # flag for point selection
        self.receiving=False

        # flag for selection made or not 
        self.selected=False

        # point of interest
        self.pointOfInterest=None
    
    def setPointOfInterest(self, poi):
        self.pointOfInterest=poi

class VideoScreen(QMainWindow):
    __instance = None
    @staticmethod
    def getInstance():
        if VideoScreen.__instance == None:
            VideoScreen()
        return VideoScreen.__instance

    def __init__(self, parent):
        # one person tracker
        self.onePersonTracker=None

        # message box for goal
        self.goalMessage=None

        # point list
        self.courtPoints=[]

        if VideoScreen.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            VideoScreen.__instance = self
        super(VideoScreen, self).__init__()
        self.showMaximized()
        self.params = None
        self.videoPath = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self,parent)
    
        self.VBL = self.ui.verticalLayout
        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)
        #slider
        #self.ui.verticalLayout.addWidget(self.ui.slider)
        self.videoGiven = self.videoPath is not None

        if self.videoPath is not None:
            self.startVideoWorker()

        # mouse click configs
        #self.FeedLabel.setStyleSheet("background-color: rgb(255,0,0)")
        self.FeedLabel.parent().resize(*IMAGE_SIZE)
        # x_movement = 150
        # for button in self.findChildren(QPushButton):
        #     button.move(button.x()+x_movement, button.y())
        # checkBox = self.findChild(QCheckBox)
        # checkBox.move(checkBox.x()+x_movement, checkBox.y())


        # init One Person Tracker Class Object
        self.onePersonTracker = OnePersonTracker()

        # goal message box
        self.goalMessage = QMessageBox()
        self.goalMessage.setText("Goal!!")
        self.setWindowTitle("Goal Notification Window")

        #stylesheet
        self.setStyleSheet(
            """
            QLabel {
                opacity:0.1;
                border-radius:3px;
                border: 2px solid black;
            }
            """
            
        )

    #mouse click
    def mousePressEvent(self, event):

        if self.FeedLabel.pixmap() and (event.button() == QtCore.Qt.LeftButton):
            #print(self.FeedLabel.pixmap().width(), " : ", self.FeedLabel.pixmap().height())
            if len(self.courtPoints) < 4:
                area = self.FeedLabel
                parent = area.parent()
                parent.setStyleSheet("border: 2px solid red;")

                x_stride = parent.x()
                y_stride = parent.y()
                rel_x = event.x()-x_stride
                rel_y = event.y()-y_stride

                #slider = self.findChildren(QSlider)[0]
                ## slider yüzünden noktalar kayıyor
                ## hata çözümüne bakılacak 
                #print(slider.geometry())
                #print(self.FeedLabel.geometry())
                #print(parent.geometry())


                bottomRight = area.geometry().bottomRight()
                x_limit = bottomRight.x()
                y_limit = bottomRight.y()
                if (rel_x>=0) and (rel_y>=0) and (rel_x<x_limit) and (rel_y<y_limit):
                    #print("relative coordinates: ",rel_x, rel_y)
                    self.courtPoints.append((rel_x, rel_y))

            # if receiving poi, set it
            if self.onePersonTracker.receiving:
                area = self.FeedLabel
                parent = area.parent()
                x_stride = parent.x()
                y_stride = parent.y()
                rel_x = event.x()-x_stride
                rel_y = event.y()-y_stride

                self.onePersonTracker.setPointOfInterest((rel_x, rel_y))
                # set selected True 
                self.onePersonTracker.receiving=False
                self.onePersonTracker.selected=True
                # reset button to receive another point
                self.prepareSelection()
                        
            
        elif self.FeedLabel.pixmap() and (event.button() == QtCore.Qt.RightButton):
            self.courtPoints=[]
            self.Worker1.courtPoints = []
        


    # when video ends
    def resetContent(self):
        print("Reset Content")
        self.StopFeed()


    def goalNotification(self):
        print("Goal!!!")
        if self.ui.goal_label.isVisible() is False:
            self.ui.changeGoalVisibilty()
    
    def stopGoalNotification(self):
        if self.ui.goal_label.isVisible():
            self.ui.changeGoalVisibilty()

    def drawLines(self, image):
        #print(image.shape)
        first = []
        second = []
        other = []
        for i in self.courtPoints[1:]:
            if self.courtPoints[0][1] - 40 < i[1] < self.courtPoints[0][1] + 40:
                first = i
            elif  self.courtPoints[0][0] - 240 <i[0] < self.courtPoints[0][0] + 240:
                second = i
            else:
                other = i
        if len(self.courtPoints) == 4:
            cv2.line(image, self.courtPoints[0], first, (255,0,0), 2)
            cv2.line(image, self.courtPoints[0], second, (255,0,0), 2)
            cv2.line(image, other, first, (255,0,0), 2)
            cv2.line(image, other, second, (255,0,0), 2)
        return image

    def openVideo(self):
        # test
        #self.FeedLabel.clear()
        if self.FeedLabel.pixmap():
            self.FeedLabel.pixmap().detach()
            self.Worker1.terminate()

        self.initLoadingGif()
        self.startVideoWorker()

        #slider = self.findChildren(QSlider)[0]
        #slider.setMaximum(int(self.Worker1.cap.get(cv2.CAP_PROP_FRAME_COUNT)))

    # stop video when slider pressed
    def sliderPressedStop(self):
        self.Worker1.stop()

    # slider released event
    def sliderUpdateFrame(self):
        print("slider release")
        self.setPosition()
        self.Worker1.stop()
        

    def prepareSelection(self):
        button = self.findChildren(QPushButton, "onePersonTrack")[0]
        if not self.onePersonTracker.selected:
            # relevant button
            button.setEnabled(False)
            button.setText("Select POI")
        else:
            button.setEnabled(True)
            button.setText("One Person Track")
    
    def resetOnePersonTrack(self):
        self.onePersonTracker.setPointOfInterest(None)
        self.onePersonTracker.selected=False
        self.onePersonTracker.receiving=False

        button = self.findChildren(QPushButton, "resetOnePersonTrack")[0]
        button.setEnabled(False)


    def onePersonTrack(self):
        # if another point selected before, reset variables
        if self.onePersonTracker.pointOfInterest is not None:
            self.onePersonTracker.selected=False
            self.onePersonTracker.setPointOfInterest(None)

        self.prepareSelection()
        self.onePersonTracker.receiving=True
        self.findChildren(QPushButton, "resetOnePersonTrack")[0].setEnabled(True)
        
    def setPosition(self):
        frame_position = self.findChildren(QSlider)[0].sliderPosition()
        self.Worker1.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)

        

    def initLoadingGif(self):
        self.loading = QMovie("loading.gif")
        
        #resize qlabel
        self.FeedLabel.setMovie(self.loading)
        self.FeedLabel.resize(*GIF_SIZE)
        self.FeedLabel.setAlignment(Qt.AlignCenter)
        
        #start gif
        self.loading.start()
        self.loading.setScaledSize(QSize(*GIF_SIZE))

    def startLoadingGif(self):
        # start gif
        if self.loading.state()==0:
            self.loading.start()
        else:
            pass

    def stopLoadingGif(self):
        if self.loading.state()==2:
            self.FeedLabel.resize(*IMAGE_SIZE)
            self.loading.stop()
        else:
            pass

    def startVideoWorker(self):
        self.Worker1 = Worker1(self.videoPath, self, self.courtPoints, self.onePersonTracker)
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.ResetContent.connect(self.resetContent)
        self.Worker1.StartLoading.connect(self.startLoadingGif)
        self.Worker1.StopLoading.connect(self.stopLoadingGif)
        self.Worker1.GoalNotification.connect(self.goalNotification)
        self.Worker1.StopGoalNotification.connect(self.stopGoalNotification)
        self.Worker1.HyperParameters = self.params
        
    def ImageUpdateSlot(self, frame):
        # draw court lines
        
        frame = self.drawLines(frame)
        # convert pyqt version 
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        Image = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
        #Pic = ConvertToQtFormat.scaled(1200, 840, Qt.KeepAspectRatio)
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

        # update slider
        #slider = self.findChildren(QSlider)[0]
        #slider.setValue(slider.sliderPosition()+1)

        # set QLabel parent widget size
        p_width = self.FeedLabel.pixmap().width()
        p_height = self.FeedLabel.pixmap().height()
        self.FeedLabel.parent().resize(p_width, p_height)


    def StopFeed(self):
        if self.videoPath is not None:
            self.Worker1.stop()
        else:
            print("işlem yapmak için video seçip ilerleyiniz")

    def Forward(self):
        if self.videoPath is not None:
            self.Worker1.forward()
        else:
            print("işlem yapmak için video seçip ilerleyiniz")

    def Backward(self):
        if self.videoPath is not None:
            self.Worker1.backward()
        else:
            print("işlem yapmak için video seçip ilerleyiniz")

    def TrackState(self, state):
        if self.videoPath is not None:
            self.Worker1.doTrack = (state == QtCore.Qt.Checked)
        else:
            print("işlem yapmak için video seçip ilerleyiniz")
    def setParameters(self, params):
        self.params = params

# class IntroWindow(QWidget):
#     def __init__(self,parent):
#         super(IntroWindow, self).__init__()
#         self.path = ""
#         self.ui = Ui_IntroWindow()
#         self.ui.setupUi(self,parent)

class StatisticWindow(QWidget):
    def __init__(self):
        super(StatisticWindow, self).__init__()
        self.ui = Ui_StatisticWindow()
        self.ui.setupUi(self)
        
class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.videoTab = VideoScreen(self)
        self.statsTab = StatisticWindow()
        self.tabs.resize(300,200)
        
        self.tabs.addTab(self.videoTab,"Video")
        self.tabs.addTab(self.statsTab,"İstatistik")
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
    
    def transferPath(self):
        self.videoTab.startVideoWorker()
    
    def changeTab(self, index):
        self.tabs.setCurrentIndex(index)

class WrapperWindow(QMainWindow):
    def __init__(self):
        super(WrapperWindow, self).__init__()
        self.showMaximized()
        self.centralwidget = MyTableWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.ui = Ui_WrapperWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WrapperWindow()
    window.show()
    sys.exit(app.exec_())
