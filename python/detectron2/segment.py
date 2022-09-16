# Copyright (c) Facebook, Inc. and its affiliates.
import numpy as np
import torch
import os
import cv2
import argparse
from loguru import logger
from sys import platform
from pathlib import Path
from detectron2.config import get_cfg
from predictor import Predictor
from tracker import DetectedInstance, SimpleTracker
from yolox.tracker.byte_tracker import BYTETracker
from torchvision import ops, utils

# constants
WINDOW_NAME = "COCO detections"
CONFIDENCE_THRESHOLD = 0.50

def get_color(idx):
    idx = idx * 3
    color = ((37 * idx) % 255, (17 * idx) % 255, (29 * idx) % 255)
    return color

def get_auto_ckpt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/model_final_f10217.pkl"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/model_final_f10217.pkl"
    return filename

class Argument:
    track_thresh = 0.5
    track_buffer = 30
    mot20 = False
    match_thresh = 0.8
    aspect_ratio_thresh = 1.6
    min_box_area = 10.0

class InstanceSegmentation:
    def __init__(self, arg):
        try:
            print("__init__", arg)

            ckpt_file = None
            fp16 = True 
            self.simple = False
            self.draw_overlay = False


            unpacked_args = arg[0].split(",")
            for line in unpacked_args:
                key_value = line.split("=")
                print("key  ", key_value[0])
                print("value", key_value[1])
                if key_value[0] == "ckpt_file":
                    ckpt_file = key_value[1]
                if key_value[0] == "fp16":
                    fp16 = not key_value[1].lower() == "false"
                if key_value[0] == "simple":
                    self.simple = key_value[1].lower() == "true"
                if key_value[0] == "overlay":
                    self.draw_overlay = key_value[1].lower() == "true"

            print("class InstanceSegmentation initialized with the values from command line")
            print("ckpt_file", ckpt_file)
            print("fp16", fp16)
            print("simple", self.simple)
            print("overlay", self.draw_overlay)

            if ckpt_file is not None:
                if ckpt_file.lower() == "auto":
                    ckpt_file = get_auto_ckpt_filename()
                    print("ckpt_file:", ckpt_file)
                    cache = Path(ckpt_file)

                    if not cache.is_file():
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        torch.hub.download_url_to_file("https://sourceforge.net/projects/avio/files/model_final_f10217.pkl/download", ckpt_file)

            cfg = get_cfg()
            cfg.merge_from_file('./detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml')
            cfg.MODEL.RETINANET.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = CONFIDENCE_THRESHOLD
            #cfg.MODEL.WEIGHTS = './detectron2/models/COCO-InstanceSegmentation/model_final_f10217.pkl'
            cfg.MODEL.WEIGHTS = ckpt_file
            cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = CONFIDENCE_THRESHOLD
            cfg.freeze()

            self.tracker = None
            if self.simple:
                self.tracker = SimpleTracker()
            else:
                self.tracker = BYTETracker(Argument())
            self.predictor = Predictor(cfg, fp16)
        except:
            logger.exception("Instance Segmentation initialization error")
            raise


    def __call__(self, arg):
        try:
            img = arg[0][0]

            predictions = self.predictor(img)["instances"]
            masks = predictions.pred_masks
            box_tensor = predictions.pred_boxes.to(torch.device('cpu')).tensor
            classes = predictions.pred_classes.to(torch.device('cpu')).numpy()
            scores = predictions.scores.to(torch.device('cpu'))
            img_tensor = torch.from_numpy(img).to(torch.device('cuda'))
            color_mask = torch.zeros_like(img_tensor).to(torch.device('cuda'))
            composite_mask = torch.zeros_like(img_tensor).to(torch.device('cuda'))

            if self.simple:

                boxes = box_tensor.numpy()
                detected = []
                for i in range(len(predictions)):
                    detected.append(DetectedInstance(classes[i], boxes[i], mask_rle=None, color=None, ttl=8))

                if len(detected):
                    colors = self.tracker.assign_colors(detected)

                    for i in range(len(masks)):
                        mask = masks[i].int()

                        color = (colors[i] * 255).astype(int)

                        red_map = torch.zeros_like(mask, dtype=torch.uint8).to(torch.device('cuda'))
                        red_map += mask * color[0]
                        green_map = torch.zeros_like(mask, dtype=torch.uint8).to(torch.device('cuda'))
                        green_map += mask * color[1]
                        blue_map = torch.zeros_like(mask, dtype=torch.uint8).to(torch.device('cuda'))
                        blue_map += mask * color[2]

                        color_mask += torch.stack((red_map, green_map, blue_map), 2)

                    img = color_mask.to(torch.device('cpu')).numpy()
            else:
                bboxes = torch.column_stack((predictions.pred_boxes.to(torch.device('cpu')).tensor, scores))

                indices = torch.from_numpy(np.where((classes == 0) | (classes == 2))[0])
                bboxes = torch.index_select(bboxes, 0, indices)

                if bboxes is not None:
                    targets = self.tracker.update(bboxes, [img.shape[0], img.shape[1]], (img.shape[0], img.shape[1]))

                if self.draw_overlay:
                    colors = []
                    for i in range(masks.size()[0]):
                        colors.append((0, 0, 0))

                    for t in targets:
                        box = np.asarray(t.tlwh).astype(np.int32)
                        box[2:] += box[:2]
                        box = np.expand_dims(box, 0)
                        iou = ops.box_iou(torch.from_numpy(box), predictions.pred_boxes.to(torch.device('cpu')).tensor)
                        index = int(torch.argmax(iou).item())

                        colors[index] = get_color(t.track_id)

                    masks.to(torch.device('cpu'))
                    img_tensor = torch.permute(torch.from_numpy(img), (2, 0, 1))
                    img_tensor = utils.draw_segmentation_masks(img_tensor, masks, 0.5, colors)
                    img = torch.permute(img_tensor, (1, 2, 0)).numpy()

                else:
                    colors = []
                    track_ids = []
                    for i in range(masks.size()[0]):
                        colors.append((0, 0, 0))
                        track_ids.append(0)

                    for t in targets:
                        box = np.asarray(t.tlwh).astype(np.int32)
                        box[2:] += box[:2]
                        box = np.expand_dims(box, 0)
                        iou = ops.box_iou(torch.from_numpy(box), predictions.pred_boxes.to(torch.device('cpu')).tensor)
                        index = int(torch.argmax(iou).item())

                        mask = masks[index].int()
                        composite_mask += torch.stack((mask, mask, mask), 2)
                        
                        colors[index] = get_color(t.track_id)
                        track_ids[index] = t.track_id

                    composite_mask = torch.gt(composite_mask, 0.0)
                    img_tensor *= composite_mask
                    img = img_tensor.to(torch.device('cpu')).numpy()

                    for idx, box in enumerate(bboxes):
                        p1 = (int(box[0]), int(box[1]))
                        p2 = (int(box[2]), int(box[3]))
                        cv2.putText(img, str(track_ids[idx]), p1, cv2.FONT_HERSHEY_PLAIN, 1, colors[idx], 1)
                        cv2.rectangle(img, p1, p2, colors[idx], 1)

            return img

        except:
            logger.exception("Instance Segmentation runtime error")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="detectron2 detection")
    parser.add_argument("filename", metavar="filename", type=ascii, help="picture file for input")
    parser.add_argument("checkpoint", metavar="checkpoint", type=ascii, help="checkpoint filename for model")
    args = parser.parse_args()

    segment = InstanceSegmentation(('ckpt_file=' + eval(args.checkpoint),),)
    img = cv2.imread(eval(args.filename))
    img = segment(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
