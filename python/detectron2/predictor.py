import cv2
import torch

from loguru import logger

from detectron2.checkpoint import DetectionCheckpointer
from detectron2.modeling import build_model
class Predictor:

    def __init__(self, cfg, fp16=False):
        print("DefaultPredictor.__init__")
        self.cfg = cfg.clone()
        self.model = build_model(self.cfg)

        checkpointer = DetectionCheckpointer(self.model)
        checkpointer.load(cfg.MODEL.WEIGHTS)
        self.model.eval()
        self.fp16 = fp16
        if self.fp16:
            print("Enabling model for fp16")
            self.model.half()

    def __call__(self, original_image):
        with torch.no_grad():
            height, width = original_image.shape[:2]

            aspect = float(width) / float(height)
            if aspect > 1.0:
                target_width = min(width, self.cfg.INPUT.MAX_SIZE_TEST)
                target_height = int(target_width / aspect)
            else:
                target_height = min(height, self.cfg.INPUT.MAX_SIZE_TEST)
                target_width = int(target_height * aspect)

            image = cv2.resize(original_image, (target_width, target_height))
            if self.fp16:
                image = torch.as_tensor(image.astype("float16").transpose(2, 0, 1))
            else:
                image = torch.as_tensor(image.astype("float32").transpose(2, 0, 1))

            inputs = {"image": image, "height": height, "width": width}
            predictions = self.model([inputs])[0]
            return predictions
