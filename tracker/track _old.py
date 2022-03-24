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
import numpy as np
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
        self.yolo_model = 'best_6.pt'
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

class MyTracker:
    def __init__(self, cap, source):
        self.opt = Arguments(source)
        self.dataset, self.device, self.model, self.webcam, self.deepsort, self.dt, self.names, self.save_txt, self.show_vid, self.seen, self.doTrack, self.videoRolling = initialize(self.opt, cap)

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

    # The MOT16 evaluation runs multiple inference streams in parallel, each one writing to
    # its own .txt file. Hence, in that case, the output folder is not restored
    # if not evaluate:
    #     if os.path.exists(out):
    #         pass
    #         shutil.rmtree(out)  # delete output folder
    #     os.makedirs(out)  # make new output folder

    # Directories
    # save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    # save_dir.mkdir(parents=True, exist_ok=True)  # make dir

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



def detect(opt,cap, tracker):
    global ball
    counter = 0
    videoRolling = True
    doTrack = True

    def findBoudry(point, f,s,o):
        global max_x, max_y, min_x, min_y
        max_x = max(point[0], f[0], s[0] , o[0])
        min_x = min(point[0], f[0], s[0] , o[0])
        max_y = max(point[1], f[1], s[1] , o[1])
        min_y = min(point[1], f[1], s[1] , o[1])

    def check_goal(ball_coords,frame):
        global goal_counter
        if len(ball_coords)>1:
            ball_center_x = (ball_coords[0] + ball_coords[2]) / 2 
            ball_center_y = (ball_coords[1] + ball_coords[3]) / 2
            # ball_center_y =ball_coords[3]
            if  max_y + 50 > ball_center_y > max_y - 50:
                goal_counter +=1 
            if  min_y - 50 < ball_center_y < min_y + 50:
                goal_counter +=1
            else:
                goal_counter = 0
            cv2.line(frame, (ball_coords[0], ball_coords[1]), (ball_coords[2], ball_coords[3]), (229,204,255), 2)

    def draw_line(frame, win_name):
        global points
        cv2.setMouseCallback(win_name, on_mouse)
        first = []
        second = []
        other = []
        for i in points[1:]:
            if points[0][1] - 40 < i[1] < points[0][1] + 40:
                first = i
            elif  points[0][0] - 240 <i[0] < points[0][0] + 240:
                second = i
            else:
                other = i
        if len(points) > 3:
            cv2.line(frame, points[0], first, (255,0,0), 2)
            cv2.line(frame, points[0], second, (255,0,0), 2)
            cv2.line(frame, other, first, (255,0,0), 2)
            cv2.line(frame, other, second, (255,0,0), 2)
            findBoudry(points[0], first, second, other)
        # return points[0], first, second, other
    def on_mouse(event,x,y,flags,params):

        global rect,startPoint,endPoint,points
        # get mouse click
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append([x, y])
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            points = list([])

    dataset, device, save_dir, model, webcam, deepsort, dt, half, names, save_txt, txt_path, show_vid, seen = initialize(opt, cap)
    

def process_frame(opt, frame, resized_img, tracker):
    img = torch.from_numpy(resized_img).to(tracker.device)
    img = img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
            img = img.unsqueeze(0)
    t2 = time_sync()
    # Inference
    #visualize = increment_path(tracker.save_dir / Path(path).stem, mkdir=True) if opt.visualize else False
    print("shape!!!!",img.shape)
    pred = tracker.model(img)#, visualize=visualize)
    t3 = time_sync()
    tracker.dt[1] += t3 - t2
    
    # Apply NMS
    pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, opt.classes, opt.agnostic_nms, max_det=opt.max_det)
    tracker.dt[2] += time_sync() - t3

    im0 = frame
    # Process detections
    # buraya bakılacak
    for i, det in enumerate(pred):  # detections per image
        tracker.seen += 1
        
        """
        p = Path(p)  # to Path
        save_path = str(tracker.save_dir / p.name)  # im.jpg, vid.mp4, ...
        s += '%gx%g ' % img.shape[2:]  # print string
        """
        annotator = Annotator(im0, line_width=2, pil=not ascii)

        if det is not None and len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(
                img.shape[2:], det[:, :4], im0.shape).round()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                #s += f"{n} {tracker.names[int(c)]}{'s' * (n > 1)}, "  # add to string

            xywhs = xyxy2xywh(det[:, 0:4])
            confs = det[:, 4]
            clss = det[:, 5]

            # pass detections to deepsort
            t4 = time_sync()
            outputs = tracker.deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), im0)
            t5 = time_sync()
            tracker.dt[3] += t5 - t4

            # draw boxes for visualization
            if len(outputs) > 0 and tracker.doTrack:
                for j, (output, conf) in enumerate(zip(outputs, confs)):
                    
                    bboxes = output[0:4]
                    
                    id = output[4]
                    cls = output[5]

                    c = int(cls)  # integer class
                    label = f'{id} {tracker.names[c]} {conf:.2f}'
                    if 'Ball' in label:
                        ball = bboxes
                    else:
                        ball = []
                    annotator.box_label(bboxes, label, color=colors(c, True))


                    # if tracker.save_txt:
                    #     # to MOT format
                    #     bbox_left = output[0]
                    #     bbox_top = output[1]
                    #     bbox_w = output[2] - output[0]
                    #     bbox_h = output[3] - output[1]
                        
                    #     with open(f"ballCoord.txt", "a") as f:
                    #         myStr = f'{(bboxes, id, cls, c, label)}\n'
                            
                    #         if cls == 0:
                    #             myStr = f'{(bboxes)}\n'
                    #             f.write(myStr)

                    #     with open(tracker.txt_path, 'a') as f:
                    #         f.write(('%g ' * 10 + '\n') % (tracker.counter + 1, id, bbox_left,  # MOT format
                    #                                     bbox_top, bbox_w, bbox_h, -1, -1, -1, -1))

            # LOGGER.info(f'{s}Done. YOLO:({t3 - t2:.3f}s), DeepSort:({t5 - t4:.3f}s)')

        else:
            tracker.deepsort.increment_ages()
            LOGGER.info('No detections')

        # Stream results
        im0 = annotator.result()
        #check_goal(ball,im0)
        #if goal_counter > 0:
        #    print(goal_counter)
        #cv2.imshow(str(p), im0)
    return im0
        



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--yolo_model', nargs='+', type=str, default='best_6.pt', help='model.pt path(s)')
    parser.add_argument('--deep_sort_model', type=str, default='osnet_x0_25')
    parser.add_argument('--source', type=str, default='gol1.mp4', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='inference/output', help='output folder')  # output folder
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.3, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--show-vid', default=True, action='store_true', help='display tracking video results')
    parser.add_argument('--save-vid', default=False, action='store_true', help='save video tracking results')
    parser.add_argument('--save-txt', default=True, action='store_true', help='save MOT compliant results to *.txt')
    # class 0 is person, 1 is bycicle, 2 is car... 79 is oven
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 16 17')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--evaluate', action='store_true', help='augmented inference')
    parser.add_argument("--config_deepsort", type=str, default="deep_sort/configs/deep_sort.yaml")
    parser.add_argument("--half", action="store_true", help="use FP16 half-precision inference")
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detection per image')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--project', default=ROOT / 'runs/track', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand

    cap = cv2.VideoCapture('gol2.mp4')
    with torch.no_grad():
        detect(opt,cap)
