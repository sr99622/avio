# Copyright (c) Facebook, Inc. and its affiliates.
import numpy as np
import torch
import cv2
import math
import os
import argparse
from loguru import logger
from sys import platform
from pathlib import Path
from detectron2.config import get_cfg
from predictor import Predictor
from tracker import DetectedInstance, SimpleTracker
from yolox.tracker.byte_tracker import BYTETracker
from torchvision import ops

# constants
CONFIDENCE_THRESHOLD = 0.50

def get_color(idx):
    idx = idx * 3
    color = ((37 * idx) % 255, (17 * idx) % 255, (29 * idx) % 255)
    return color

def get_auto_ckpt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/model_final_a6e10b.pkl"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/model_final_a6e10b.pkl"
    return filename

def draw_keypoint(img, keypoint, color):
    color = (int(color[0]), int(color[1]), int(color[2]))
    kp = keypoint[:, :2]
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
    cv2.line(img, right_ankle, right_knee, color, 3)
    cv2.line(img, left_knee, left_hip, color, 3)
    cv2.line(img, right_knee, right_hip, color, 3)
    cv2.line(img, left_hip, right_hip, color, 3)
    cv2.line(img, mid_hip, mid_shoulder, color, 3)
    cv2.line(img, left_shoulder, right_shoulder, color, 3)
    cv2.line(img, left_shoulder, left_elbow, color, 3)
    cv2.line(img, right_shoulder, right_elbow, color, 3)
    cv2.line(img, left_elbow, left_wrist, color, 3)
    cv2.line(img, right_elbow, right_wrist, color, 3)
    cv2.circle(img, nose, head_radius, color, 3)

class Argument:
    track_thresh = 0.5
    track_buffer = 30
    mot20 = False
    match_thresh = 0.8
    aspect_ratio_thresh = 1.6
    min_box_area = 10.0

class Keypoint:
    def __init__(self, arg):
        try:
            print("__init__", arg)

            ckpt_file = None
            fp16 = True
            self.no_back = False
            self.simple = False

            unpacked_args = arg[0].split(",")
            for line in unpacked_args:
                key_value = line.split("=")
                print("key  ", key_value[0])
                print("value", key_value[1])
                if key_value[0] == "ckpt_file":
                    ckpt_file = key_value[1]
                if key_value[0] == "fp16":
                    fp16 = not key_value[1].lower() == "false"
                if key_value[0] == "no_back":
                    self.no_back = key_value[1].lower() == "true"
                if key_value[0] == "simple":
                    self.simple = key_value[1].lower() == "true"

            print("class Keypoint initialized with the values from command line")
            print("ckpt_file", ckpt_file)
            print("fp16", fp16)
            print("no_back", self.no_back)
            print("simple", self.simple)

            if ckpt_file is not None:
                if ckpt_file.lower() == "auto":
                    ckpt_file = get_auto_ckpt_filename()
                    print("ckpt_file:", ckpt_file)
                    cache = Path(ckpt_file)

                    if not cache.is_file():
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        torch.hub.download_url_to_file("https://sourceforge.net/projects/avio/files/model_final_a6e10b.pkl/download", ckpt_file)

            cfg = get_cfg()
            cfg.merge_from_file('./detectron2/configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml')
            cfg.MODEL.RETINANET.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            #cfg.MODEL.WEIGHTS = './detectron2/models/COCO-Keypoints/model_final_a6e10b.pkl'
            cfg.MODEL.WEIGHTS = ckpt_file
            cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = CONFIDENCE_THRESHOLD
            cfg.freeze()

            self.tracker = None
            if self.simple:
                print("using simple tracker")
                self.tracker = SimpleTracker()
            else:
                print("using bytetrack")
                self.tracker = BYTETracker(Argument())
            self.predictor = Predictor(cfg, fp16)
        except:
            logger.exception("Keypoints initialization error")
            raise


    def __call__(self, arg):
        try:
            img = arg[0][0]

            predictions = self.predictor(img)["instances"].to(torch.device('cpu'))
            keypoints = predictions.pred_keypoints.numpy().astype(np.int)

            if self.no_back:
                img = np.zeros_like(img)

            if self.simple:
                boxes = predictions.pred_boxes.tensor.numpy()
                classes = predictions.pred_classes.numpy()

                detected = []
                for i in range(len(predictions)):
                    detected.append(DetectedInstance(classes[i], boxes[i], mask_rle=None, color=None, ttl=8))

                if len(detected):
                    colors = np.asarray(self.tracker.assign_colors(detected)) * 255
                    colors = colors.astype(np.int32)
                    for idx, keypoint in enumerate(keypoints):
                        draw_keypoint(img, keypoint, colors[idx])

            else:
                bboxes = torch.column_stack((predictions.pred_boxes.tensor, predictions.scores))
                
                if bboxes is not None:
                    targets = self.tracker.update(bboxes, [img.shape[0], img.shape[1]], (img.shape[0], img.shape[1]))
                
                    for t in targets:
                        box = np.asarray(t.tlwh).astype(np.int32)
                        box[2:] += box[:2]
                        box = np.expand_dims(box, 0)
                        iou = ops.box_iou(torch.from_numpy(box), predictions.pred_boxes.tensor)
                        index = int(torch.argmax(iou).item())
                        draw_keypoint(img, keypoints[index], get_color(t.track_id))

            return img

        except:
            logger.exception("Keypoints runtime error")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="detectron2 detection")
    parser.add_argument("filename", metavar="filename", type=ascii, help="picture file for input")
    parser.add_argument("checkpoint", metavar="checkpoint", type=ascii, help="checkpoint filename for model")
    args = parser.parse_args()

    keypoint = Keypoint(('ckpt_file=' + eval(args.checkpoint),),)
    img = cv2.imread(eval(args.filename))
    img = keypoint(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
