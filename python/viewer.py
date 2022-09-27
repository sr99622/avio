import os
import sys
import cv2
import numpy as np
import torch
import pickle
from loguru import logger
import qdarktheme

from box import Box

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
    QCheckBox,
)

from PyQt6.QtGui import (
    QImage,
    QPixmap,
    QKeyEvent,
)

from PyQt6.QtCore import (
    QSettings,
    Qt,
)

class ViewerWindow(QWidget):
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            sys.exit()
        return super().keyPressEvent(event)

class ListWidget(QListWidget):

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.currentRowChanged.connect(self.changed)

    def populate(self):
        self.clear()
        files = os.listdir(self.mainWindow.directory)
        for file in files:
            self.addItem(file)

    def changed(self, row):
        print("changed", row)
        try:
            item = self.currentItem()
            if item is not None:
                print(item.text())
                image = np.asarray(cv2.imread(self.mainWindow.directory + "/" + item.text()))
                frame = Box(image.shape[:2], "shape")

                if self.mainWindow.chkProcess.isChecked():
                    segments = self.mainWindow.segment.predict(image)
                    mask = segments.pred_masks[0]
                    #box = segments.pred_boxes[0].tensor.numpy().astype(int)[0]
                    focus = Box(segments.pred_boxes[0].tensor.numpy().astype(int)[0], "xyxy")
                    #x1, y1, x2, y2 = box
                    print("focus height", focus.h)
                    #box_center = [x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2]
                    img_tensor = torch.from_numpy(image)
                    img_tensor *= torch.stack((mask, mask, mask), 2)


                    #blur_tensor = torch.from_numpy(blur)
                    #blur_tensor *= torch.stack((~mask, ~mask, ~mask), 2)
                    #img_tensor += blur_tensor

                    image = img_tensor.numpy()

                    kpts = self.mainWindow.keypoint.predict(image)[0]
                    kpts[:, 2] = kpts[:, 2] > 0.6
                    #body_points = sum(kpts[:, 2][5:])
                    #face_points = sum(kpts[:, 2][:5])
                    #count = sum(kpts[:, 2])
                    nose = kpts[0][:2].astype(int)
                    nose_distance = [nose[0] - frame.center()[0], nose[1] - frame.y1]
                    print("nose_distance", nose_distance)

                    #for pt in kpts:
                    #    x_coord, y_coord, conf = pt.astype(int)
                    #    if conf:
                    #        cv2.circle(image, (x_coord, y_coord), 4, (255, 255, 255), -1)
                    #        cv2.rectangle(image, focus.tl(), focus.br(), (255, 255, 255), 1)
                    x_coord, y_coord, conf = kpts[0].astype(int)
                    cv2.circle(image, (x_coord, y_coord), 4, (255, 255, 255), 1)

                qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_BGR888)
                pixmap = QPixmap(qimage)
                self.mainWindow.lblImage.setPixmap(pixmap)
        except Exception as error:
            logger.exception(error)

class MainWindow(ViewerWindow):

    def __init__(self):
        super().__init__()

        self.settings = QSettings("avio", "Image Viewer")
        self.directory = self.settings.value("directory", os.path.expanduser("~"))

        self.lblImage = QLabel(self)
        self.lblImage.setMinimumWidth(256)
        self.lblImage.setMinimumHeight(512)

        self.btnReverse = QPushButton("<<", self)
        self.btnReverse.clicked.connect(self.reverse)

        self.btnForward = QPushButton(">>", self)
        self.btnForward.clicked.connect(self.forward)

        self.btnRun = QPushButton("Run", self)
        self.btnRun.clicked.connect(self.run)

        self.lstFiles = ListWidget(self)
        self.lstFiles.populate()

        self.txtDirectory = QLineEdit(self.directory, self)
        self.btnSelect = QPushButton("...", self)
        self.btnSelect.setMaximumWidth(40)
        self.btnSelect.clicked.connect(self.selectDir)

        self.chkProcess = QCheckBox("Process Image", self)
        self.chkProcess.setChecked(self.settings.value("chkProcess", False, type=bool))
        self.chkProcess.clicked.connect(self.checkProcess)

        layout = QGridLayout()
        layout.addWidget(self.lblImage,       0, 0, 5, 1)
        layout.addWidget(self.txtDirectory,   0, 2, 1, 5)
        layout.addWidget(self.btnSelect,      0, 7, 1, 1)
        layout.addWidget(self.lstFiles,       1, 2, 5, 6)
        layout.addWidget(self.chkProcess,     6, 0, 1, 2)
        layout.addWidget(self.btnReverse,     6, 2, 1, 2)
        layout.addWidget(self.btnForward,     6, 4, 1, 2)
        layout.addWidget(self.btnRun,         6, 6, 1, 2)
        self.setLayout(layout)
        self.keypoint = Keypoint(('ckpt_file=auto',),)
        self.segment = InstanceSegmentation(('ckpt_file=auto',),)

        if self.lstFiles.count() > 0:
            self.lstFiles.setCurrentRow(0)
            self.lstFiles.setFocus()

    def reverse(self):
        print("reverse")

    def forward(self):
        row = self.lstFiles.currentRow()
        print("row", row)
        if (row < self.lstFiles.count() - 1):
            item = self.lstFiles.currentItem()
            if item is not None:
                print(item.text())
                self.lstFiles.setCurrentRow(row + 1)

        print("forward")

    def run(self):
        print("run")
        try:
            nose_distances = []
            box_dims = []
            for i in range(self.lstFiles.count()):
                item = self.lstFiles.item(i)
                print(item.text())
                image = np.asarray(cv2.imread(self.directory + "/" + item.text()))
                frame = Box(image.shape[:2], "shape")
                segments = self.segment.predict(image)
                if len(segments.pred_masks) > 0:
                    mask = segments.pred_masks[0]
                    #box = segments.pred_boxes[0].tensor.numpy()[0]
                    focus = Box(segments.pred_boxes[0].tensor.numpy()[0], "xyxy")

                    #box_dim = [box[3] - box[1], (box[3] - box[1]) / (box[2] - box[0])]
                    #print("box_dim", box_dim)
                    #box_dims.append(box_dim)
                    #x1, y1, x2, y2 = box.astype(int)
                    #box_center = [x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2]
                    img_tensor = torch.from_numpy(image)
                    img_tensor *= torch.stack((mask, mask, mask), 2)
                    image = img_tensor.numpy()
                    kpts = self.keypoint.predict(image)
                    if kpts is not None:
                        kpts = kpts[0]
                        nose = kpts[0][:2].astype(int)
                        nose_distance = [nose[0] - frame.center()[0], nose[1] - frame.y1]
                        nose_distances.append(nose_distance)
                        print("nose_distance", nose_distance)

            nose_result = np.stack(nose_distances, axis=0)
            nose_mean = np.mean(nose_result, 0)
            nose_std = np.std(nose_result, 0)
            print("mean", nose_mean)
            print("std", nose_std)

            #box_result = np.stack(box_dims, axis=0)
            #box_mean = np.mean(box_result, 0)
            #box_std = np.std(box_result, 0)
            #print("box_mean", box_mean)
            #print("box_std", box_std)

        except Exception as error:
            logger.exception(error)

    def selectDir(self):
        self.directory = QFileDialog.getExistingDirectory(None, "Open Directory", self.txtDirectory.text())
        self.txtDirectory.setText(self.directory)
        self.settings.setValue("directory", self.directory)
        self.lstFiles.populate()
        self.lstFiles.setCurrentRow(0)

    def checkProcess(self):
        self.settings.setValue("chkProcess", self.chkProcess.isChecked())
        self.lstFiles.changed(self.lstFiles.currentRow())

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()