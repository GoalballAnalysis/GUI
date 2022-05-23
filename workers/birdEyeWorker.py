
import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import os

IMAGE_PATH=os.path.join("./assets", "pitch.png")
WIDTH=400
HEIGHT=800 # with goals included 914

# stride values for drawing pitch image, image bigger than the pitch
STRIDE_X=201 
STRIDE_Y=101

class BirdEyeWorker(): #QThread
    def __init__(self, courtPoints):
        #super().__init__()
        # sort court points to be used in edge conditions
        courtPoints=self.sort_court_points(courtPoints)

        self.courtPoints=np.float32(courtPoints)
        self.original_image=BirdEyeWorker.read_image()
        self.updatable_image=self.original_image.copy()

        self.image_coordinates=np.float32(
            [
                [0,0],
                [WIDTH,0],
                [0,HEIGHT],
                [WIDTH,HEIGHT]
            ]
        )
        # calculating transform matrix
        self.matrix=cv2.getPerspectiveTransform(self.courtPoints, self.image_coordinates)


    def sort_court_points(self, courtPoints):
        """
        [x_2, x_3, x_1, x_4]
        [y_2, y_1, y_4, y_3]
        """
        print(f"before sort: {courtPoints}")
        courtPoints=sorted(courtPoints, key = lambda x: x[0])
        courtPoints=[courtPoints[1], courtPoints[2], courtPoints[0], courtPoints[3]]
        print(f"after sort: {courtPoints}")
        return courtPoints

    def draw_on_pitch(self, image, point, color):
        point=(
            point[0]+STRIDE_X,
            point[1]+STRIDE_Y
        )
        image=cv2.circle(image, point, 2, color, 2)
        return image

    def convert_point(self, point):
        point_vector=np.array(
            [  
                point[0],
                point[1],
                1
            ]
        )
        x_, y_, _ = self.matrix @ point_vector # np.dot()
        
        transformed_point=(
            round(x_/_),
            round(y_/_)
        )
        return transformed_point

    def reset_updatable(self):
        self.updatable_image=self.original_image.copy()

    def read_image():
        img=cv2.imread(IMAGE_PATH)
        return img

    def bbox2point(self, bbox):
        """
        [763 192 832 265   1   1]
        [xmin, ymin, xmax, ymax, id, is_human]
        """
        x_= (bbox[0]+bbox[2])//2
        y_= max(bbox[1], bbox[3])
        return (x_, y_)


    def bird_eye_view(self, points):
        self.reset_updatable()
        """     
        points=[
            [578,211],
            [613,214],
            [326,498],
            [611,459],
            [924,494],
            [705, 220], # ball
            [731, 153], # outside
            [768, 195],  # goal
            [803, 191], # goal 2
            [707, 544], # goal 3
            [112, 548], # goal post  bottom left
            [154, 261], # outside 1
            [99, 196], # outside 2
            [596, 324] # center
        ]
        """
        color=(255,0,0)
        for point in points:
            is_ball=point[-1]==0
            point=self.bbox2point(point)
            new_point=self.convert_point(point)
            print(new_point)
            """
            if is_ball:
                color=(0, 255, 0)
            """
            self.updatable_image=self.draw_on_pitch(self.updatable_image, new_point, color)

        return self.updatable_image





if __name__=="__main__":
    points=[
        (299, 205),
        (916, 202),
        (127, 519),
        (1089, 516)
    ]
    worker=BirdEyeWorker(points)
    worker.run()

    