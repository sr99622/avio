# Copyright (c) Facebook, Inc. and its affiliates.
import cv2
import torch
import numpy as np
from loguru import logger
from sys import platform
import os
import argparse
from pathlib import Path
from detectron2.config import get_cfg
from predictor import Predictor
from tracker import DetectedInstance, SimpleTracker
from yolox.tracker.byte_tracker import BYTETracker

# constants
CONFIDENCE_THRESHOLD = 0.5

def get_color(idx):
    idx = idx * 3
    color = ((37 * idx) % 255, (17 * idx) % 255, (29 * idx) % 255)

    return color

class Argument:
    track_thresh = 0.5
    track_buffer = 30
    mot20 = False
    match_thresh = 0.8
    aspect_ratio_thresh = 1.6
    min_box_area = 10.0

def get_auto_ckpt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/model_final_280758.pkl"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/model_final_280758.pkl"
    return filename

class Detection:
    def __init__(self, arg):
        print("Detection.__init__")

        try:
            ckpt_file = None
            fp16 = True
            self.simple = False

            if arg is not None:
                unpacked_args = arg[0].split(",")
                for line in unpacked_args:
                    key_value = line.split("=")
                    print("key  ", key_value[0])
                    print("value", key_value[1])
                    if key_value[0] == 'ckpt_file':
                        ckpt_file = key_value[1]
                    if key_value[0] == 'fp16':
                        fp16 = not key_value[1].lower() == "false"
                    if key_value[0] == "simple":
                        self.simple = key_value[1].lower() == "true"

            print("class Keypoint initialized with the values from command line")
            print("ckpt_file", ckpt_file)
            print("fp16", fp16)
            print("simple", self.simple)

            if ckpt_file is not None:
                if ckpt_file.lower() == "auto":
                    ckpt_file = get_auto_ckpt_filename()
                    print("ckpt_file:", ckpt_file)
                    cache = Path(ckpt_file)

                    if not cache.is_file():
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        torch.hub.download_url_to_file("https://sourceforge.net/projects/avio/files/model_final_280758.pkl/download", ckpt_file)

            cfg = get_cfg()
            cfg.merge_from_file('./detectron2/configs/COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml')
            cfg.MODEL.RETINANET.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = CONFIDENCE_THRESHOLD
            #cfg.MODEL.WEIGHTS = './detectron2/models/COCO-Detection/model_final_280758.pkl'
            cfg.MODEL.WEIGHTS = ckpt_file
            cfg.MODEL.MASK_ON = False
            cfg.freeze()

            self.tracker = None
            if self.simple:
                self.tracker = SimpleTracker()
            else:
                self.tracker = BYTETracker(Argument())
            self.predictor = Predictor(cfg, fp16=fp16)

            print("Detection initialization complete")

        except:
            logger.exception("Detections initialization failure")
            raise

    def __call__(self, arg):

        try:
            img = arg[0][0]

            predictions = self.predictor(img)["instances"].to(torch.device('cpu'))
            classes = predictions.pred_classes.numpy()
            
            text_scale = 1
            text_thickness = 1
            line_thickness = 2

            if self.simple:
                boxes = predictions.pred_boxes.tensor.numpy().astype(np.int32)

                detected = []
                for i in range(len(predictions)):
                    detected.append(DetectedInstance(classes[i], boxes[i], mask_rle=None, color=None, ttl=8))

                if len(detected):
                    colors = np.asarray(self.tracker.assign_colors(detected)) * 255
                    colors = colors.astype(np.int32)

                    for idx, box in enumerate(boxes):
                        r, g, b = colors[idx]
                        color = (int(r), int(g), int(b))
                        cv2.rectangle(img, box[:2], box[2:], color=color, thickness=line_thickness)

            else:
                bboxes = torch.column_stack((predictions.pred_boxes.tensor, predictions.scores))

                # use these lines to filter out classes in bbox tensor
                #indices = torch.from_numpy(np.where((classes == 0) | (classes == 2))[0])
                #bboxes = torch.index_select(bboxes, 0, indices)
                indices = torch.from_numpy(np.where((classes == 0))[0])
                bboxes = torch.index_select(bboxes, 0, indices)

                if bboxes is not None:
                    targets = self.tracker.update(bboxes, [img.shape[0], img.shape[1]], (img.shape[0], img.shape[1]))
                
                    for t in targets:
                        box = np.asarray(t.tlwh).astype(np.int32)
                        box[2:] += box[:2]
                        color = get_color(t.track_id)
                        cv2.rectangle(img, box[:2], box[2:], color=color, thickness=line_thickness)
                        cv2.putText(img, str(t.track_id), box[:2], cv2.FONT_HERSHEY_PLAIN, text_scale, (0, 0, 255),
                                    thickness=text_thickness)

            return img
            
        except:
            logger.exception("Detection run time failure")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="detectron2 detection")
    parser.add_argument("filename", metavar="filename", type=ascii, help="picture file for input")
    parser.add_argument("checkpoint", metavar="checkpoint", type=ascii, help="checkpoint filename for model")
    args = parser.parse_args()

    detect = Detection(('ckpt_file=' + eval(args.checkpoint),),)
    img = cv2.imread(eval(args.filename))
    img = detect(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
