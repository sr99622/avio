import torchvision
import torch
import cv2
import numpy as np
import torchvision.transforms as transforms

transform = transforms.Compose([
    transforms.ToTensor(),
])

class RetinaNet:
    def __init__(self):
        print("RetinaNet.__init__")
        self.min_size = 800
        self.threshold = 0.35
        self.model = torchvision.models.detection.retinanet_resnet50_fpn(pretrained=True,  min_size=self.min_size)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.eval().to(self.device)

    def __call__(self, arg):
        img = arg[0][0]
        tensor = transform(img).to(self.device)
        tensor = tensor.unsqueeze(0)

        with torch.no_grad():
            outputs = self.model(tensor)

        scores = outputs[0]['scores'].detach().cpu().numpy()
        labels = outputs[0]['labels'].detach().cpu().numpy()
        boxes = outputs[0]['boxes'].detach().cpu().numpy()
        labels = labels[np.array(scores) >= self.threshold]
        boxes = boxes[np.array(scores) >= self.threshold].astype(np.int32)
        boxes = boxes[np.array(labels) == 1]

        for box in boxes:
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (255, 255, 255), 1)

        return img

