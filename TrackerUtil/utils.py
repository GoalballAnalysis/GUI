from tkinter.messagebox import NO
import numpy as np
import cv2
from time import sleep
from tracker.track import *

cap = None

def setCap(excap):
    cap = excap

def open_video(path):
    cap = cv2.VideoCapture(path)
    tracker = get_tracker(cap, path)
    return tracker, cap

def main(tracker, doTrack):

    tracker.opt.doTrack = doTrack
    frame = process_frame(tracker)
    
    return frame
    


cv2.destroyAllWindows()