from models.experimental import attempt_load
from utils.torch_utils import select_device
from utils.general import check_img_size, non_max_suppression
from utils.datasets import letterbox

from numpy import random
import torch
import cv2
import numpy as np

class Detection:
    def __init__(self, arg):
        print("Detection.__init__")
        self.device = select_device('0')
        self.model = attempt_load('yolov7/detection/yolov7.pt', map_location=self.device)
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

            pred = self.model(img, False)[0]
            pred = non_max_suppression(pred)[0]

            for det in pred:
                np_det = det.cpu().numpy()
                x1 = int((np_det[0] - border[0]) / ratio[0])
                y1 = int((np_det[1] - border[1]) / ratio[1])
                x2 = int((np_det[2] - border[0]) / ratio[0])
                y2 = int((np_det[3] - border[1]) / ratio[1])
                cv2.rectangle(raw_img, (x1, y1), (x2, y2), (255, 255, 255), 2)

            return raw_img

if __name__ == "__main__":
    det = Detection("ckpt_file=auto")
    img = cv2.imread("C:/Users/stephen/Pictures/test.jpg")
    img = det(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
