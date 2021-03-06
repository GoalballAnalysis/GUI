# limit the number of cpus used by high performance libraries
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.insert(0, './yolov5')

import argparse
import os
import platform
import shutil
import time
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn

from yolov5.models.experimental import attempt_load
from yolov5.utils.downloads import attempt_download
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import LoadImages
from yolov5.utils.general import (LOGGER, check_img_size, non_max_suppression, scale_coords, 
                                  check_imshow, xyxy2xywh, increment_path)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator, colors
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort
from workers.birdEyeWorker import BirdEyeWorker


# goal notification duration (suggested to be the same as REPLAY_BUTTON_DURATION)
GOAL_NOTIFICATION_DURATION=4
# default fps 30
FPS=30

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 deepsort root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

points = list()
max_y = 0
min_y = 0
max_x = 0
min_x = 0
ball = []
goal_counter = 0




class Arguments:
    def __init__(self, source):
        self.yolo_model = 'best-185-epoch.pt'#'28_03.pt'
        self.deep_sort_model = 'osnet_x0_25'
        self.source = source
        self.output = 'inference/output'
        self.imgsz = [640, 640]
        self.conf_thres = 0.3
        self.iou_thres = 0.5
        self.fourcc = 'mp4v'
        self.device = ''
        self.show_vid = True
        self.save_vid = False
        self.save_txt = True
        self.config_deepsort = "deep_sort/configs/deep_sort.yaml"
        self.max_det = 1000
        self.project = ROOT
        self.name = 'exp'
        self.classes=None
        
        self.counter=0
        self.videoRolling=True
        self.doTrack=True

class MyTracker:
    def __init__(self, cap, source):

        # goal notification display duration counter (assume 30 fps)
        self.goal_notification_counter=None
        self.bird_eye_worker=None

        self.opt = Arguments(source)
        self.cap = cap
        self.dataset, self.device, self.model, self.webcam, self.deepsort, self.dt, self.names, self.save_txt, self.show_vid, self.seen, self.doTrack, self.videoRolling = initialize(self.opt, cap)
        self.half=False

    def init_bird_eye(self, courtPoints):
        self.bird_eye_worker=BirdEyeWorker(courtPoints)
        


def initialize(opt, cap):
    source, yolo_model, deep_sort_model, show_vid, save_txt, imgsz, project, name= opt.source, opt.yolo_model, opt.deep_sort_model, opt.show_vid, opt.save_txt, opt.imgsz, opt.project, opt.name
    webcam = source == '0' or source.startswith(
        'rtsp') or source.startswith('http') or source.endswith('.txt')

    # initialize deepsort
    cfg = get_config()
    cfg.merge_from_file(opt.config_deepsort)
    deepsort = DeepSort(deep_sort_model,
                        max_dist=cfg.DEEPSORT.MAX_DIST,
                        max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                        max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                        use_cuda=True)

    # Initialize
    device = select_device(opt.device)
    #half &= device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(yolo_model, device=device)#, dnn=opt.dnn)
    stride, names, pt, jit, _ = model.stride, model.names, model.pt, model.jit, model.onnx
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Half
    # half &= pt and device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
    if pt:
        model.model.float()

    # Set Dataloader
    vid_path, vid_writer = None, None
    # Check if environment supports image displays
    if show_vid:
        show_vid = check_imshow()

    # Dataloader
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit, cap=cap)
    bs = 1  # batch_size
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names

    # extract what is in between the last '/' and last '.'
    # txt_file_name = source.split('/')[-1].split('.')[0]
    # txt_path = str(Path(save_dir)) + '/' + txt_file_name + '.txt'

    if pt and device.type != 'cpu':
        model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
    dt, seen = [0.0, 0.0, 0.0, 0.0], 0

    return dataset, device, model, webcam, deepsort, dt, names, save_txt, show_vid, seen, True, True



def resetBoundries():
    global max_x, max_y, min_x, min_y
    max_x = min_x = max_y = min_y = 0

def findBoudry(points):
    base = points[0]
    first = []
    second = []
    other = []
    for i in points[1:]:
        if base[1] - 40 < i[1] < base[1] + 40:
            first = i
        elif  base[0] - 240 <i[0] < base[0] + 240:
            second = i
        else:
            other = i
    global max_x, max_y, min_x, min_y
    max_x = max(base[0], first[0], second[0] , other[0])
    min_x = min(base[0], first[0], second[0] , other[0])
    max_y = max(base[1], first[1], second[1] , other[1])
    min_y = min(base[1], first[1], second[1] , other[1])

def check_goal(ball_coords,frame, thresholds):
    global goal_counter
    if len(ball_coords)>0:
        ball_center_x = (ball_coords[0] + ball_coords[2]) / 2 
        ball_center_y = (ball_coords[1] + ball_coords[3]) / 2
        upLineAbove = thresholds[0]
        upLineBelow = thresholds[1]
        lowLineAbove = thresholds[2]
        lowLineBelow = thresholds[3]
        
        if  max_y + lowLineBelow > ball_center_y > max_y - lowLineAbove:
            goal_counter +=1 
        elif  min_y - upLineAbove < ball_center_y < min_y + upLineBelow:
            goal_counter +=1
        else:
            goal_counter = 0
        cv2.line(frame, (ball_coords[0], ball_coords[1]), (ball_coords[2], ball_coords[3]), (229,204,255), 2)


def filterDetections(detections, onePersonTracker):
    poi = onePersonTracker.pointOfInterest
    
    filtered=[]
    closest = None
    min_distance = 1000
    if onePersonTracker.selected:
        for detection in detections:
            if detection[5] == 1:
                coords = detection[:4]
                mid_x = (coords[0]+coords[2])//2
                mid_y = (coords[1]+coords[3])//2
                distance = (((poi[0]-mid_x)**2)+((poi[1]-mid_y)**2))**.5
                if min_distance>distance:
                    min_distance=distance
                    closest=detection
                    
                    # update point of interest
                    onePersonTracker.setPointOfInterest((mid_x, mid_y))
            else:
                filtered.append(detection)


    filtered.append(closest)
    return filtered

def process_frame(tracker, show=False, courtPoints = None, onePersonTracker=None, params=[35, 15, 35, 30, 60]):
    global ball, goal_counter

    # initialize bird eye if not yet
    if len(courtPoints)>0 and (tracker.bird_eye_worker is None):
        print(f"court points: {courtPoints}")
        tracker.init_bird_eye(courtPoints)


    if params is None:
        params=[35, 15, 35, 30, 60]
    """
    onePerson is boolean value 
    determines whether we track one person or not
    """
    if onePersonTracker:
        onePerson = onePersonTracker.selected


    if tracker.opt.videoRolling:
        if tracker.opt.counter == 0 and show:
            tracker.opt.videoRolling = False
        try:
            path, img, im0s, vid_cap, s = tracker.dataset.__next__()
        except StopIteration:
            # video ended
            return None
        tracker.opt.counter+=1
        t1 = time_sync()
        img = torch.from_numpy(img).to(tracker.device)
        img = img.half() if tracker.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        t2 = time_sync()
        tracker.dt[0] += t2 - t1

        # Inference
        pred = tracker.model(img)#, augment=opt.augment, visualize=visualize)
        t3 = time_sync()
        tracker.dt[1] += t3 - t2

        # Apply NMS
        pred = non_max_suppression(pred, tracker.opt.conf_thres, tracker.opt.iou_thres, tracker.opt.classes, False, max_det=tracker.opt.max_det)
        tracker.dt[2] += time_sync() - t3


        # Process detections
        for i, det in enumerate(pred):  # detections per image
            tracker.seen += 1
            
            p, im0, _ = path, im0s.copy(), getattr(tracker.dataset, 'frame', 0)

            #p = Path(p)  # to Path
            #save_path = str(save_dir / p.name)  # im.jpg, vid.mp4, ...
            #s += '%gx%g ' % img.shape[2:]  # print string

            annotator = Annotator(im0, line_width=2, pil=not ascii)

            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {tracker.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                xywhs = xyxy2xywh(det[:, 0:4])
                confs = det[:, 4]
                clss = det[:, 5]

                # pass detections to deepsort
                t4 = time_sync()
                outputs = tracker.deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), im0)
                t5 = time_sync()
                tracker.dt[3] += t5 - t4


                # ball filtering uygulanacak
                # print(tracker.names)
                # draw boxes for visualization

                # if one person tracking option selected
                # then filter detections and show only one person
                if onePerson:
                    outputs = filterDetections(outputs, onePersonTracker)

                

                labels=[]
                chosen=False
                if len(outputs) > 0 and tracker.opt.doTrack:
                    for j, (output, conf) in enumerate(zip(outputs, confs)):
                        
                        try:
                            bboxes = output[0:4]
                            id = output[4]
                            cls = output[5]
                        except:
                            # this part will be executed just for one time right after resetOnePersonTrack button is clicked 
                            continue
                        
                        c = int(cls)  # integer class
                        label = f'{id} {tracker.names[c]} {conf:.2f}'
                        labels.append(tracker.names[c])
                        if 'Ball' in label:
                            if not chosen:
                                ball = bboxes
                                chosen=True
                        annotator.box_label(bboxes, label, color=colors(c, True))
                    if "Ball" not in labels:
                        ball=[]


                """
                Bird Eye View Image initialization
                """
                # bird eye viewing creation
                bird_eye_frame=None
                # bird eye view filtering part
                if tracker.bird_eye_worker is not None:
                    bird_eye_frame=tracker.bird_eye_worker.bird_eye_view(outputs)

            else:
                tracker.deepsort.increment_ages()
                LOGGER.info('No detections')

            # Stream results
            im0 = annotator.result()
            #check_goal(ball,im0)
            ##
            if goal_counter > 0:
                print(goal_counter)
            
            if tracker.opt.show_vid:   
                if show:

                    cv2.imshow(str(p), im0)
                else:
                    
                    upLineAbove = params[0]
                    upLineBelow = params[1]
                    lowLineAbove = params[2]
                    lowLineBelow = params[3]
                    cv2.line(im0, (15, max_y - lowLineAbove),(1115, max_y - lowLineAbove), (120,134,255), 2)
                    cv2.line(im0, (15, max_y + lowLineBelow),(1115, max_y + lowLineBelow), (120,134,255), 2)
                    cv2.line(im0, (15, min_y - upLineAbove),(1115, min_y - upLineAbove), (255,0,0), 2)
                    cv2.line(im0, (15, min_y + upLineBelow),(1115, min_y + upLineBelow), (255,0,0), 2)

                    if len(courtPoints)  == 4:
                        findBoudry(courtPoints)
                    else:
                        resetBoundries()
                    check_goal(ball, im0, params[:-1])


                    # handle goal notification counter
                    if (tracker.goal_notification_counter is None) and (goal_counter>=params[-1]):
                        # if counter not initialized and goal counter decided for a goal

                        # we were not reset gol_counter and it was sending goal notification
                        # more than once to the gui module which controls replay button
                        # now goal_notification_counter handles the goal notification label
                        # and returning goal or not depends on it while it starts from 1 
                        # because we control it right after initialization (that case it can
                        # not start from 0, it may cause blinking errors on replay button) 
                        tracker.goal_notification_counter=1

                    if tracker.goal_notification_counter is not None:
                        tracker.goal_notification_counter+=1
                        if tracker.goal_notification_counter>=(GOAL_NOTIFICATION_DURATION*FPS): # assume 30 fps
                            tracker.goal_notification_counter=None
                            goal_counter=0


                    # set bird eye view image as base court image if it is None
                    if bird_eye_frame is None:
                        bird_eye_frame=BirdEyeWorker.read_image()

                    if tracker.goal_notification_counter is not None:
                        # if frame counter did not pass the limit (GOAL_NOTIFICATION_DURATION)
                        return (im0, bird_eye_frame), True
                    else:
                        return (im0, bird_eye_frame), False                        
                
                
                key = cv2.waitKey(5)
                if key == ord('q'):  # q to quit
                    raise StopIteration
                elif  key == ord('s'):
                    tracker.opt.videoRolling = not tracker.opt.videoRolling
                elif  key == ord('t'):
                    tracker.opt.doTrack = not tracker.opt.doTrack
                    

    else:
        key = cv2.waitKey(5)
        if key == ord('q'):  # q to quit
            raise StopIteration
        elif  key == ord('s'):
            tracker.opt.videoRolling = not tracker.opt.videoRolling
    
def get_tracker(cap, source):
    tracker = MyTracker(cap, source)
    return tracker



if __name__ == '__main__':
    source = 'gol2.mp4'
    cap = cv2.VideoCapture(source)
    tracker = get_tracker(cap, source)
    while True:
       process_frame(tracker, True)