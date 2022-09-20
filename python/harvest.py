import os
import sys
import cv2
import numpy as np
import torch

from loguru import logger

sys.path.append("bytetrack")
sys.path.append("yolov7/keypoint")
sys.path.append("detectron2")

from interface import ByteTrack
from keypoint import Keypoint
from segment import InstanceSegmentation

class Track:
    def __init__(self, rts):
        self.missed_counts = 0
        self.saved = False
        self.last_rts = rts

class Harvest:
    def __init__(self, arg):
        print("Harvest.__init__")
        self.bytetrack = ByteTrack(("trt_file=auto",),)
        self.keypoint = Keypoint(("ckpt_file=auto",),)
        self.segment = InstanceSegmentation(("ckpt_file=auto",),)
        self.desired_width = 256
        self.desired_height = 512
        self.active_tracks = {}
        self.img_count = 0

    def __call__(self, arg):
        try:
            orig_img = arg[0][0]
            rts = arg[2][0]
            img = np.ascontiguousarray(np.copy(orig_img))
            online_targets = self.bytetrack.predict(img)
            linesize = 2

            if online_targets is not None:
                for t in online_targets:
                    tlwh = t.tlwh
                    track_id = int(t.track_id)
                    id_text = '{}'.format(int(track_id)).zfill(5)
                    color = ((37 * track_id) % 255, (17 * track_id) % 255, (29 * track_id) % 255)

                    x, y, w, h = tlwh
                    box = tuple(map(int, (x, y, x + w, y + h)))
                    x1, y1, x2, y2 = box
                    y1 = max(y1, 0)
                    x1 = max(x1, 0)
                    y2 = min(y2, img.shape[0])
                    x2 = min(x2, img.shape[1])
                    w = x2 - x1
                    h = y2 - y1

                    if h > 512 and h / w > 2.0:

                        #adjust box boundaries to fill the resolution normalized rectangle
                        projected_height = int(h * 1.1)
                        delta_y = projected_height - h
                        y1 = y1 - int(delta_y / 2)
                        y2 = y2 + int(delta_y / 2)

                        projected_width = projected_height / 2
                        delta_x = projected_width - w
                        x1 = x1 - int(delta_x / 2)
                        x2 = x2 + int(delta_x / 2)

                        if x1 > 0 and x2 < img.shape[1] and y1 > 0 and y2 < img.shape[0]:

                            color = (255, 255, 255)
                            linesize = 4

                            if track_id in self.active_tracks.keys():
                                self.active_tracks[track_id].missed_counts = 0
                                self.active_tracks[track_id].last_rts = rts
                            else:
                                self.active_tracks.update({track_id : Track(rts)})

                            if not self.active_tracks[track_id].saved:
                                dh = self.desired_height
                                dw = self.desired_width

                                scale = dh / h
                                w = int(w * scale)

                                subject = np.zeros((dh, dw, 3), dtype=np.uint8)
                                crop = orig_img[y1:y2, x1:x2]

                                resized = cv2.resize(crop, (dw, dh), interpolation=cv2.INTER_AREA)
                                #blank[:dh, w_diff:w+w_diff, :] = resized
                                subject[:dh, :dw, :] = resized
                                test_subject = np.ascontiguousarray(np.copy(subject))

                                segments = self.segment.predict(test_subject)
                                if len(segments.pred_masks) > 0:
                                    mask = segments.pred_masks[0]
                                    img_tensor = torch.from_numpy(test_subject)
                                    img_tensor *= torch.stack((mask, mask, mask), 2)
                                    seg_img = img_tensor.numpy()
                                    kpts = self.keypoint.predict(seg_img)
                                    if kpts is not None:
                                        kpts[0][:, 2] = kpts[0][:, 2] > 0.5
                                        body_points = sum(kpts[0][:, 2][5:])
                                        face_points = sum(kpts[0][:, 2][:5])
                                        if body_points == 12.0 and face_points == 5.0:
                                            print("GOT IT")
                                            rts_text = '{}'.format(int(rts)).zfill(7)
                                            self.img_count += 1
                                            count_text = '{}'.format(int(self.img_count)).zfill(4)
                                            self.active_tracks[track_id].saved = True
                                            filename = "C:/Users/stephen/Pictures/42nd/" + rts_text + "_" + count_text + ".jpg"
                                            cv2.imwrite(filename, subject)


        

                    # manage tracked objects dictionary
                    tracks_to_be_removed = []
                    for id in self.active_tracks:
                        if self.active_tracks[id].last_rts != rts:
                            self.active_tracks[id].missed_counts += 1
                            if self.active_tracks[id].missed_counts > 30:
                                tracks_to_be_removed.append(id)
                    for id in tracks_to_be_removed:
                        self.active_tracks.pop(id)

                    #print("active_tracks size:", len(self.active_tracks))

                    cv2.rectangle(img, box[0:2], box[2:4], color, linesize)
                    cv2.putText(img, id_text, (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            return cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)
        except Exception as error:
            logger.exception("Harvest run time error")
            print(error)