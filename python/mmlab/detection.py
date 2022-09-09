import cv2
import numpy as np
import mmcv
from mmdet.apis import inference_detector, init_detector

class Detection:
    def __init__(self, arg):
        print("Detect.__init__")
        config = "mmlab/configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py"
        ckpt = "mmlab/checkpoints/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"
        device = "cuda:0"
        self.model = init_detector(config, ckpt, device=device)

    def __call__(self, arg):
        #print("Detect.__call__")
        img = arg[0][0]
        results = inference_detector(self.model, img)
        # results is a list the size of classes with each element an array of bboxes
        bboxes = results[0]
        for box in bboxes:
            if box[4] > 0.3:
                p1 = (int(box[0]), int(box[1]))
                p2 = (int(box[2]), int(box[3]))
                cv2.rectangle(img, p1, p2, (255, 255, 255), 1)
        return img

if __name__ == "__main__":
    detection = Detection("ckpt_file=auto")
    img = cv2.imread("C:/Users/stephen/Pictures/test.jpg")
    img = detection(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)