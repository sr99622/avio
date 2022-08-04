# Copyright (c) Facebook, Inc. and its affiliates.
import numpy as np
import torch

from loguru import logger

from detectron2.config import get_cfg
from predictor import Predictor
from tracker import DetectedInstance, SimpleTracker

# constants
WINDOW_NAME = "COCO detections"
CONFIDENCE_THRESHOLD = 0.50

class InstanceSegmentation:
    def __init__(self, arg):
        try:
            print("__init__", arg)
            cfg = get_cfg()
            cfg.merge_from_file('./detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml')
            cfg.MODEL.RETINANET.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.WEIGHTS = './detectron2/models/COCO-InstanceSegmentation/model_final_f10217.pkl'
            cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = CONFIDENCE_THRESHOLD
            cfg.freeze()

            self.tracker = SimpleTracker()
            self.predictor = Predictor(cfg, True)
        except:
            logger.exception("Instance Segmentation initialization error")
            raise


    def __call__(self, arg):
        try:
            img = arg[0][0]

            predictions = self.predictor(img)["instances"]
            masks = predictions.pred_masks

            boxes = predictions.pred_boxes.to(torch.device('cpu')).tensor.numpy()
            classes = predictions.pred_classes.to(torch.device('cpu')).numpy()

            detected = []
            for i in range(len(predictions)):
                detected.append(DetectedInstance(classes[i], boxes[i], mask_rle=None, color=None, ttl=8))

            colors = self.tracker.assign_colors(detected)

            img_tensor = torch.from_numpy(img).to(torch.device('cuda'))
            total_map = torch.zeros_like(img_tensor).to(torch.device('cuda'))

            for i in range(len(masks)):
                mask = masks[i].int()

                color = (colors[i] * 160).astype(int)

                red_map = torch.zeros_like(mask, dtype=torch.uint8).to(torch.device('cuda'))
                red_map += mask * color[0]
                green_map = torch.zeros_like(mask, dtype=torch.uint8).to(torch.device('cuda'))
                green_map += mask * color[1]
                blue_map = torch.zeros_like(mask, dtype=torch.uint8).to(torch.device('cuda'))
                blue_map += mask * color[2]

                total_map += torch.stack((red_map, green_map, blue_map), 2)

            #img = img_tensor.to(torch.device('cpu')).numpy()
            img = total_map.to(torch.device('cpu')).numpy()
            return img

        except:
            logger.exception("Instance Segmentation runtime error")
            raise
