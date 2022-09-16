import cv2
import torch
import argparse
import os
from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.plots import plot_one_box, colors
from utils.torch_utils import select_device
from sys import platform
from pathlib import Path
import numpy as np

def get_auto_ckpt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/yolov7-w6-pose.pt"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/yolov7-w6-pose.pt"
    return filename

class Keypoint:
    def __init__(self, arg):
        print("Keypoint.__init__", arg)
        #'''

        ckpt_file = None

        unpacked_args = arg[0].split(",")
        for line in unpacked_args:
            key_value = line.split("=")
            print("key  ", key_value[0])
            print("value", key_value[1])
            if key_value[0] == "ckpt_file":
                ckpt_file = key_value[1]


        if ckpt_file is not None:
            if ckpt_file.lower() == "auto":
                ckpt_file = get_auto_ckpt_filename()
                print("cpkt_file:", ckpt_file)
                cache = Path(ckpt_file)

                if not cache.is_file():
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    torch.hub.download_url_to_file("https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7-w6-pose.pt", ckpt_file)

        with torch.no_grad():
            self.imgsz = 640
            self.kpt_label = True
            self.conf_thres = 0.01
            self.iou_thres = 0.45
            self.classes = None
            self.agnostic = False
            opt_device = '0'

            self.device = select_device(opt_device)
            self.half = self.device.type != 'cpu'

            print("ckpt", ckpt_file)
            self.model = attempt_load(ckpt_file, map_location=self.device)  # load FP32 model
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
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="yolov7 keypoint")
    parser.add_argument("filename", metavar="filename", type=ascii, help="picture file for input")
    parser.add_argument("checkpoint", metavar="checkpoint", type=ascii, help="checkpoint filename for model")
    args = parser.parse_args()

    keypoint = Keypoint(('ckpt_file=' + eval(args.checkpoint),),)
    img = cv2.imread(eval(args.filename))
    img = keypoint(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
