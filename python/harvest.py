import os
import sys
import cv2
import numpy as np
import torch

from box import Box
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
        try:
            print("Harvest.__init__")
            self.bytetrack = ByteTrack(("trt_file=auto",),)
            self.keypoint = Keypoint(("ckpt_file=auto",),)
            self.segment = InstanceSegmentation(("ckpt_file=auto",),)
            self.desired_width = 256
            self.desired_height = 512
            self.active_tracks = {}
            self.img_count = 0
            self.dir = "C:/Users/stephen/Pictures/42nd/"
            self.conf_thresh = 0.5
        except Exception as error:
            logger.exception(error)

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

                    # det is the detection box from bytetrack
                    det = Box(tlwh, "tlwh")

                    if det.h > self.desired_height and det.h / det.w > 2.0:

                        #pad the box
                        padded_height = int(det.h * 1.1)
                        padded_width = padded_height / 2
                        det.growTo(padded_width, padded_height)

                        # make sure the padded det box is inside the frame
                        if det.within(Box(img.shape[:2], "shape")):

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

                                subject = np.zeros((dh, dw, 3), dtype=np.uint8)
                                crop = orig_img[det.y1:det.y2, det.x1:det.x2]

                                #resized = cv2.resize(crop, (dw, dh), interpolation=cv2.INTER_AREA)
                                #subject[:dh, :dw, :] = resized
                                #test_subject = np.ascontiguousarray(np.copy(subject))
                                test_subject = np.ascontiguousarray(np.copy(crop))

                                segments = self.segment.predict(test_subject)
                                if len(segments.pred_masks) > 0:
                                    # only check the first mask, this is almost always the best choice anyway
                                    mask = segments.pred_masks[0]
                                    focus = Box(segments.pred_boxes[0].tensor.numpy().astype(int)[0], "xyxy")

                                    if focus.h > self.desired_height:
                                        img_tensor = torch.from_numpy(test_subject)
                                        img_tensor *= torch.stack((mask, mask, mask), 2)
                                        seg_img = img_tensor.numpy()
                                        kpts_set = self.keypoint.predict(seg_img)
                                        if kpts_set is not None:
                                            # only check the first keypoints
                                            kpts = kpts_set[0]
                                            # keypoint confidence converted to boolean greater than threshold
                                            kpts[:, 2] = kpts[:, 2] > self.conf_thresh
                                            body_points = sum(kpts[:, 2][5:])
                                            face_points = sum(kpts[:, 2][:5])
                                            # verify full set of points over confidence threshold
                                            if body_points == 12.0 and face_points == 5.0:
                                                # align image by the nose keypoint, roughly centered
                                                nose = kpts[0][:2].astype(int)
                                                nose_test = [nose[0] - focus.center()[0], nose[1] - int(focus.y1 + 0.088 * focus.h)]
                                                print("nose_test", nose_test)
                                                print("focus", focus)
                                                x_qual = nose_test[0] > -(focus.w * 0.08) and nose_test[0] < focus.w * 0.08
                                                if x_qual:
                                                    print("X_QUAL")
                                                y_qual = nose_test[1] > -(focus.h * 0.07) and nose_test[1] < focus.h * 0.07
                                                if y_qual:
                                                    print("Y_QUAL")
                                                if x_qual and y_qual: 
                                                    # if all tests passed, write the image to file
                                                    print("det pre", det)
                                                    #nose_distance = [(nose[0] + det.x1) - det.center()[0], nose[1] - int(det.y1 + 0.086 * focus.h)]
                                                    print("nose", nose)
                                                    #nose_distance = [(nose[0] + det.x1) - det.center()[0], nose[1] - int(focus.y1 + focus.h * 0.14)]
                                                    nose_distance = [(nose[0] + det.x1) - det.center()[0], nose[1] - int(det.h * 0.15)]
                                                    det.shift(nose_distance)
                                                    print("det post", det)
                                                    subject = orig_img[det.y1:det.y2, det.x1:det.x2]
                                                    subject = cv2.resize(subject, (dw, dh), interpolation=cv2.INTER_AREA)
                                                    rts_text = '{}'.format(int(rts)).zfill(7)
                                                    self.img_count += 1
                                                    count_text = '{}'.format(int(self.img_count)).zfill(4)
                                                    self.active_tracks[track_id].saved = True
                                                    filename = self.dir + rts_text + "_" + count_text + ".jpg"
                                                    cv2.imwrite(filename, subject)
                                                    print("saved", filename)


        

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

                    cv2.rectangle(img, det.tl(), det.br(), color, linesize)
                    cv2.putText(img, id_text, det.tl(), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            return cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)
        except Exception as error:
            logger.exception("Harvest run time error")
            print(error)