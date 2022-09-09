import cv2
import torch

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.plots import plot_one_box, colors
from utils.torch_utils import select_device
import numpy as np

class Keypoint:
    def __init__(self, arg):
        print("Keypoint.__init__")
        #'''
        with torch.no_grad():
            weights = "yolov7/keypoint/yolov7-w6-pose.pt"
            view_img = True
            self.imgsz = 640
            self.kpt_label = True
            self.conf_thres = 0.01
            self.iou_thres = 0.45
            self.classes = None
            self.agnostic = False
            opt_device = '0'

            self.device = select_device(opt_device)
            self.half = self.device.type != 'cpu'

            self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
            self.stride = int(self.model.stride.max())  # model stride

            self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check img_size

            if self.half:
                self.model.half()  # to FP16

            if self.device.type != 'cpu':
                self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once
        #'''

    def __call__(self, arg):
        #'''
        im0 = arg[0][0]
        with torch.no_grad():

            img, ratio, border = letterbox(im0, self.imgsz, stride=self.stride)
            img = img[:, :, ::-1].transpose(2, 0, 1)
            img = np.ascontiguousarray(img)


            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.half else img.float() 
            img /= 255.0 
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            pred = self.model(img, False)[0]
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes=self.classes, agnostic=self.agnostic, kpt_label=self.kpt_label)

            #im0 = im0s.copy()
            for det in pred:
                if len(det):
                    scale_coords(img.shape[2:], det[:, :4], im0.shape, kpt_label=False)
                    scale_coords(img.shape[2:], det[:, 6:], im0.shape, kpt_label=self.kpt_label, step=3)
                    for det_index, (*xyxy, conf, cls) in enumerate(reversed(det[:,:6])):
                        c = int(cls) 
                        kpts = det[det_index, 6:]
                        plot_one_box(xyxy, im0, label=None, color=colors(c, True), line_thickness=1, kpt_label=self.kpt_label, kpts=kpts, steps=3, orig_shape=im0.shape[:2])

        return im0
        #'''
        

