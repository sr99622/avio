# Copyright (c) Facebook, Inc. and its affiliates.
import cv2
import torch

from loguru import logger

from detectron2.config import get_cfg
from tracker import DetectedInstance, SimpleTracker
from predictor import Predictor

# constants
CONFIDENCE_THRESHOLD = 0.5

class Detection:
    def __init__(self, arg):
        print("Detection.__init__")

        try:
            ckpt_file = None
            self.fp16 = False

            if arg is not None:
                unpacked_args = arg[0].split(",")
                for line in unpacked_args:
                    key_value = line.split("=")
                    print("key  ", key_value[0])
                    print("value", key_value[1])
                    if key_value[0] == 'ckpt_file':
                        ckpt_file = key_value[1]
                    if key_value[0] == 'fp16':
                        self.fp16 = True

            self.cfg = get_cfg()
            self.cfg.merge_from_file('./detectron2/configs/COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml')
            self.cfg.MODEL.RETINANET.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            self.cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = CONFIDENCE_THRESHOLD
            #self.cfg.MODEL.WEIGHTS = './detectron2/models/COCO-Detection/model_final_280758.pkl'
            self.cfg.MODEL.WEIGHTS = ckpt_file
            self.cfg.MODEL.MASK_ON = False
            self.cfg.freeze()

            self.predictor = Predictor(self.cfg, fp16=self.fp16)
            self.tracker = SimpleTracker()
            print("Detection initialization complete")

        except:
            logger.exception("Detections initialization failure")
            raise

    def __call__(self, arg):

        try:
            img = arg[0][0]

            predictions = self.predictor(img)["instances"].to(torch.device('cpu'))

            boxes = predictions.pred_boxes.tensor.numpy()
            classes = predictions.pred_classes.numpy()

            detected = []
            for i in range(len(predictions)):
                detected.append(DetectedInstance(classes[i], boxes[i], mask_rle=None, color=None, ttl=8))

            colors = self.tracker.assign_colors(detected)

            for i in range(len(boxes)):
                x0, y0, x1, y1 = boxes[i]
                r, g, b = (colors[i] * 255)
                color = (int(r), int(g), int(b))
                p1 = (int(x0), int(y0))
                p2 = (int(x1), int(y1))
                cv2.rectangle(img, p1, p2, color, 1)

            return img
            
        except:
            logger.exception("Detection run time failure")
            raise
