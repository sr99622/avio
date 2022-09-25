import os
import sys
import cv2
import numpy as np
import torch

sys.path.append("yolov7/keypoint")
sys.path.append("detectron2")

from keypoint import Keypoint
from segment import InstanceSegmentation

from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QPushButton,
    QListWidget,
    QLineEdit,
    QLabel,
    QWidget,
    QFileDialog,
)

from PyQt6.QtGui import (
    QImage,
    QPixmap,
)

from PyQt6.QtCore import (
    QSettings,
)

keypoint = Keypoint(('ckpt_file=auto',),)
segment = InstanceSegmentation(('ckpt_file=auto',),)

app = QApplication([])
settings = QSettings("avio", "Image Viewer")
directory = settings.value("directory", os.path.expanduser("~")).toString()
def setDir():
    directory = dir

lblImage = QLabel()
lblImage.setMinimumWidth(256)
lblImage.setMinimumHeight(512)

class ListWidget(QListWidget):
    def clicked(self, item):
        try:
            print("ListWidget:", directory + "/" + item.text())
            image = np.asarray(cv2.imread(directory + "/" + item.text()))
            blur = cv2.blur(image, (50, 50))

            predictions = segment.predict(image)
            mask = predictions.pred_masks[0]

            img_tensor = torch.from_numpy(image)
            img_tensor *= torch.stack((mask, mask, mask), 2)

            blur_tensor = torch.from_numpy(blur)
            blur_tensor *= torch.stack((~mask, ~mask, ~mask), 2)

            #img_tensor += blur_tensor
            image = img_tensor.numpy()

            #image = keypoint(((image,),))
            kpts = keypoint.predict(image)
            kpts[0][:, 2] = kpts[0][:, 2] > 0.5
            body_points = sum(kpts[0][:, 2][5:])
            face_points = sum(kpts[0][:, 2][:5])

            if body_points == 12.0:
                print("FULL BODY")
                if face_points == 5.0:
                    print("FULL FACE")
                if face_points == 4.0:
                    print("FACE 4")
                if face_points == 3.0:
                    print("FACE 3")

            for pt in kpts[0][:5]:
                x_coord, y_coord, conf = pt.astype(int)
                if conf:
                    cv2.circle(image, (x_coord, y_coord), 4, (255, 255, 255), -1)

            qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_BGR888)
            pixmap = QPixmap(qimage)

            lblImage.setPixmap(pixmap)
        except Exception as error:
            print(error)

def reverse():
    print("reverse")

def forward():
    print("forward")

def run():
    print("run")


window = QWidget()
window.setWindowTitle("QHBoxLayout")

btnReverse = QPushButton("<<")
btnReverse.clicked.connect(reverse)

btnForward = QPushButton(">>")
btnForward.clicked.connect(forward)

btnRun = QPushButton("Run")
btnRun.clicked.connect(run)

txtDirectory = QLineEdit(os.path.expanduser("~"))
def select():
    dir = QFileDialog.getExistingDirectory(
        None, "Open Directory", txtDirectory.text())
    txtDirectory.setText(dir)
    directory = dir
btnSelect = QPushButton("...")
btnSelect.setMaximumWidth(40)
btnSelect.clicked.connect(select)

lstFiles = ListWidget()
dirfiles = os.listdir(directory)
for file in dirfiles:
    lstFiles.addItem(file)
lstFiles.itemClicked.connect(lstFiles.clicked)

layout = QGridLayout()
layout.addWidget(lblImage,       0, 0, 6, 1)
layout.addWidget(txtDirectory,   0, 2, 1, 5)
layout.addWidget(btnSelect,      0, 7, 1, 1)
layout.addWidget(lstFiles,       1, 2, 5, 6)
layout.addWidget(btnReverse,     6, 2, 1, 2)
layout.addWidget(btnForward,     6, 4, 1, 2)
layout.addWidget(btnRun,         6, 6, 1, 2)
window.setLayout(layout)

window.show()
sys.exit(app.exec())