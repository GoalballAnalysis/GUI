from tkinter.messagebox import NO
from traceback import FrameSummary
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

def main(tracker, doTrack, courtPoints, onePersonTracker, params):
    """
    onePersonTracker is an object of onePersonTracker class
    """

    tracker.opt.doTrack = doTrack
    frames, goal = process_frame(tracker, courtPoints = courtPoints, onePersonTracker=onePersonTracker, params = params)
    
    return frames, goal
    


cv2.destroyAllWindows()