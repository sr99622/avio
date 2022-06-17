import torch
import cv2
import gc
import time
import numpy as np
from PIL import Image

class YoloV5:
    def __init__(self, arg):
        model_name = ""
        repo_name = ""
        width = 0
        height = 0

        unpacked_args = arg[0].split(";")
        for line in unpacked_args:
            key_value = line.split("=")
            print("key  ", key_value[0])
            print("value", key_value[1])
            if key_value[0] == "repo":
                repo_name = key_value[1]
            if key_value[0] == "model":
                model_name = key_value[1]
            if key_value[0] == "width":
                width = int(key_value[1])
            if key_value[0] == "height":
                height = int(key_value[1])

        self.model = torch.hub.load(repo_name, model_name)
        rnd_ary = np.random.randint(0, 254, (height, width, 3))
        results = self.model(rnd_ary.astype(np.uint8))
        results.print()
            

    def __call__(self, arg):
        img = arg[0][0]

        results = self.model(img).xyxy[0].to(torch.device("cpu")).numpy()
        for result in results:
            if result[5] == 0:
                p1 = (int(result[0]), int(result[1]))
                p2 = (int(result[2]), int(result[3]))
                cv2.rectangle(img, p1, p2, (255, 255, 255), 1)

        return img
