
from types import new_class
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

# court border coordinates on bird eye view image for filtering points
COURT_IMAGE_TOP_LEFT=(202, 101)
COURT_IMAGE_BOTTOM_RIGHT=(601, 901)

# borders included goals for ball filtering
COURT_IMAGE_GOALS_TOP_LEFT=(201, 43)
COURT_IMAGE_GOALS_BOTTOM_RIGHT=(601, 959)

class BirdEyeWorker(): #QThread
    def __init__(self, courtPoints):
        #super().__init__()
        # sort court points to be used in edge conditions
        courtPoints=self.sort_court_points(courtPoints)

        """
        courtPoints=[
            [0,0],
            [1280, 0],
            [0, 720],
            [1280, 720]
        ]
        """
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
        courtPoints=sorted(courtPoints, key = lambda x: x[0])
        courtPoints=[courtPoints[1], courtPoints[2], courtPoints[0], courtPoints[3]]
        return courtPoints

    def convert_pitch_size(self, point):
        point=(
            point[0]+STRIDE_X,
            point[1]+STRIDE_Y
        )
        return point

    def draw_on_pitch(self, image, point, color):
        image=cv2.circle(image, point, 3, color, 3)
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
        return (x_, y_), (bbox[-1] == 0)


    def filter_points(self, point, is_ball):
        # filter points according to their position (points in court will be filtered)
        # assign players to a different teams
        # 0 for team1, 1 for team2 and returns -1 for ball
        x_min, x_max, y_min, y_max= None, None, None, None

        if is_ball:
            """
            COURT_IMAGE_GOALS_TOP_LEFT=(201, 43)
            COURT_IMAGE_GOALS_BOTTOM_RIGHT=(601, 959)
            """
            x_max=max(COURT_IMAGE_GOALS_TOP_LEFT[0], COURT_IMAGE_GOALS_BOTTOM_RIGHT[0])
            x_min=min(COURT_IMAGE_GOALS_TOP_LEFT[0], COURT_IMAGE_GOALS_BOTTOM_RIGHT[0])
            y_max=max(COURT_IMAGE_GOALS_TOP_LEFT[1], COURT_IMAGE_GOALS_BOTTOM_RIGHT[1])
            y_min=min(COURT_IMAGE_GOALS_TOP_LEFT[1], COURT_IMAGE_GOALS_BOTTOM_RIGHT[1])

        else:
            """
            COURT_IMAGE_TOP_LEFT=(202, 101)
            COURT_IMAGE_BOTTOM_RIGHT=(601, 901)
            """
            x_max=max(COURT_IMAGE_TOP_LEFT[0], COURT_IMAGE_BOTTOM_RIGHT[0])
            x_min=min(COURT_IMAGE_TOP_LEFT[0], COURT_IMAGE_BOTTOM_RIGHT[0])
            y_max=max(COURT_IMAGE_TOP_LEFT[1], COURT_IMAGE_BOTTOM_RIGHT[1])
            y_min=min(COURT_IMAGE_TOP_LEFT[1], COURT_IMAGE_BOTTOM_RIGHT[1])

        is_inside=False

        if (point[0]<=x_max and point[0]>=x_min) and (point[1]<=y_max and point[1]>=y_min):
            # inside borders
            is_inside=True
    
        team=None
        center_y=(y_min+y_max)//2

        if is_ball:
            team=-1
        else:
            if point[1] > center_y:
                team=1
            elif point[1] <= center_y:
                team=0

        return (is_inside, team)

    def bird_eye_view(self, points):
        self.reset_updatable()
        
        """     
        # static points for test 

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

        colors=[
            (255,0,0),
            (0,0,255),
            (255,255,255)
        ]
        for point in points:
            # convert deepsort tracker bbox coordinates to standard bbox coordinates
            point, is_ball=self.bbox2point(point)
            
            # apply perspective projection on points
            new_point=self.convert_point(point)
            
            new_point=self.convert_pitch_size(new_point)
            # filter points according to their position on pitch
            passed, team=self.filter_points(new_point, is_ball)
            if not passed:
                continue
            
            color=colors[team]

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

    