# Copyright (c) Facebook, Inc. and its affiliates.
import numpy as np
import torch
import cv2
import math

from loguru import logger

from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from predictor import Predictor
from tracker import DetectedInstance, SimpleTracker

# constants
WINDOW_NAME = "COCO detections"
CONFIDENCE_THRESHOLD = 0.50

class Keypoint:
    def __init__(self, arg):
        try:
            print("__init__", arg)
            cfg = get_cfg()
            cfg.merge_from_file('./detectron2/configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml')
            cfg.MODEL.RETINANET.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.WEIGHTS = './detectron2/models/COCO-Keypoints/model_final_a6e10b.pkl'
            cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = CONFIDENCE_THRESHOLD
            cfg.freeze()

            self.tracker = SimpleTracker()
            self.predictor = Predictor(cfg, True)
        except:
            logger.exception("Keypoints initialization error")
            raise


    def __call__(self, arg):
        try:
            img = arg[0][0]

            predictions = self.predictor(img)["instances"]

            boxes = predictions.pred_boxes.to(torch.device('cpu')).tensor.numpy()
            classes = predictions.pred_classes.to(torch.device('cpu')).numpy()
            keypoints = predictions.pred_keypoints.to(torch.device('cpu')).numpy().astype(np.int)

            detected = []
            for i in range(len(predictions)):
                detected.append(DetectedInstance(classes[i], boxes[i], mask_rle=None, color=None, ttl=8))

            colors = np.asarray(self.tracker.assign_colors(detected)) * 255

            for idx, kp in enumerate(keypoints):
                color = (int(colors[idx][0]), int(colors[idx][1]), int(colors[idx][2]))
                kp = kp[:, :2]
                nose = kp[0]
                left_eye = kp[1]
                right_eye = kp[2]
                left_ear = kp[3]
                right_ear = kp[4]
                left_shoulder = kp[5]
                right_shoulder = kp[6]
                left_elbow = kp[7]
                right_elbow = kp[8]
                left_wrist = kp[9]
                right_wrist = kp[10]
                left_hip = kp[11]
                right_hip = kp[12]
                left_knee = kp[13]
                right_knee = kp[14]
                left_ankle = kp[15]
                right_ankle = kp[16]

                mid_hip = (left_hip[0] - int((left_hip[0] - right_hip[0]) / 2),
                           left_hip[1] - int((left_hip[1] - right_hip[1]) / 2))

                mid_shoulder = (left_shoulder[0] - int((left_shoulder[0] - right_shoulder[0]) / 2),
                                left_shoulder[1] - int((left_shoulder[1] - right_shoulder[1]) / 2))

                a = left_ear[0] - right_ear[0]
                b = left_ear[1] - right_ear[1]
                c = math.sqrt(a*a + b*b)
                head_radius = int(c/2)


                cv2.line(img, left_ankle, left_knee, color, 3)
                cv2.line(img, left_knee, left_hip, color, 3)
                cv2.line(img, right_ankle, right_knee, color, 3)
                cv2.line(img, right_knee, right_hip, color, 3)
                cv2.line(img, left_hip, right_hip, color, 3)
                cv2.line(img, mid_hip, mid_shoulder, color, 3)
                cv2.line(img, left_shoulder, right_shoulder, color, 3)
                cv2.line(img, left_shoulder, left_elbow, color, 3)
                cv2.line(img, left_elbow, left_wrist, color, 3)
                cv2.line(img, right_shoulder, right_elbow, color, 3)
                cv2.line(img, right_elbow, right_wrist, color, 3)
                cv2.circle(img, nose, head_radius, color, 3)


            return img

        except:
            logger.exception("Keypoints runtime error")
            raise
