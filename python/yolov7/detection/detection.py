from models.experimental import attempt_load
from utils.torch_utils import select_device
from utils.general import check_img_size, non_max_suppression
from utils.datasets import letterbox

from numpy import random
import torch
import cv2
import numpy as np
from sys import platform
import os
import argparse
from pathlib import Path

def get_auto_ckpt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/yolov7.pt"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/yolov7.pt"
    return filename


class Detection:
    def __init__(self, arg):
        print("Detection.__init__")

        ckpt_file = None

        unpacked_args = arg[0].split(',')
        for line in unpacked_args:
            key_value = line.split('=')
            print("key  ", key_value[0])
            print("value", key_value[1])
            if key_value[0] == "ckpt_file":
                ckpt_file = key_value[1]

        print("class Detection initialized with the values from command line")
        print("ckpt_file", ckpt_file)

        if ckpt_file is not None:
            if ckpt_file.lower() == "auto":
                ckpt_file = get_auto_ckpt_filename()
                cache = Path(ckpt_file)

                if not cache.is_file():
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    torch.hub.download_url_to_file("https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt", ckpt_file)


        with torch.no_grad():
            self.device = select_device('0')
            self.model = attempt_load(ckpt_file, map_location=self.device)
            self.stride = int(self.model.stride.max())
            self.imgsz=640
            self.imgsz = check_img_size(self.imgsz, s=self.stride)
            self.model.half()
            self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
            self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))
            self.old_img_w = self.old_img_h = self.imgsz
            self.old_img_b = 1

    def __call__(self, arg):
        #print("Detection.__call__")
        with torch.no_grad():
            raw_img = arg[0][0]

            img, ratio, border = letterbox(raw_img, self.imgsz, stride=self.stride)
            img = img[:, :, ::-1].transpose(2, 0, 1)
            img = np.ascontiguousarray(img)

            img = torch.from_numpy(img).to(self.device)
            img = img.half()
            img /= 255.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
 
            if (self.old_img_b != img.shape[0] or self.old_img_h != img.shape[2] or self.old_img_w != img.shape[3]):
                self.old_img_b = img.shape[0]
                self.old_img_h = img.shape[2]
                self.old_img_w = img.shape[3]
                for i in range(3):
                    self.model(img, False)[0]

            preds = self.model(img, False)[0]
            preds = non_max_suppression(preds)[0]

            for det in preds:
                np_det = det.cpu().numpy()
                if np_det[4] > 0.35:
                    #print(np_det)
                    x1 = int((np_det[0] - border[0]) / ratio[0])
                    y1 = int((np_det[1] - border[1]) / ratio[1])
                    x2 = int((np_det[2] - border[0]) / ratio[0])
                    y2 = int((np_det[3] - border[1]) / ratio[1])
                    cv2.rectangle(raw_img, (x1, y1), (x2, y2), (255, 255, 255), 2)

            return raw_img

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="yolov7 detection")
    parser.add_argument("filename", metavar="filename", type=ascii, help="picture file for input")
    parser.add_argument("checkpoint", metavar="checkpoint", type=ascii, help="checkpoint filename for model")
    args = parser.parse_args()

    detect = Detection(('ckpt_file=' + eval(args.checkpoint),),)
    img = cv2.imread(eval(args.filename))
    img = detect(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
