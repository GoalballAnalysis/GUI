from math import fabs
from shutil import which
import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import TrackerUtil.utils as tracker_utils
import tracker.track as track
from time import time
import numpy as np

class Worker1(QThread):
    def __init__(self, videoPath):
        super().__init__()
        self.tracker, self.cap = tracker_utils.open_video(videoPath)
        self.doTrack = True
    ImageUpdate = pyqtSignal(np.ndarray)
    ResetContent = pyqtSignal()
    def run(self):
        self.ThreadActive = True
        frame_rate = 60
        prev=0
        while self.ThreadActive:
            time_elapsed = (time()-prev)
            if time_elapsed > 1./frame_rate:
                frame = tracker_utils.main(self.tracker, self.doTrack)
                ret = True if (frame is not None) else False
                prev=time()
                if ret:
                    self.ImageUpdate.emit(frame)
                else:
                    self.ResetContent.emit()
            
    def stop(self):
        self.ThreadActive = not self.ThreadActive
        if self.ThreadActive:
            self.start()
            
    def forward(self):
        if self.ThreadActive:
            self.stop()

        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame +200)

        if not self.ThreadActive:
            self.stop()

    def backward(self):
        if self.ThreadActive:
            self.stop()

        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        back_temp = (current_frame-200)
        back =  back_temp if (back_temp>0) else 0
        print(back)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, back)

        if not self.ThreadActive:
            self.stop()