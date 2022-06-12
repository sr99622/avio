import tensorflow as tf
import numpy as np
import cv2
import sys

from tracker import NearestNeighborDistanceMetric
from tracker import Detection
from tracker import Tracker
from tracker import iou
from tracker import non_max_suppression

import storage


class DeepSort:

    def __init__(self, arg):
        model_name = "saved_model"
        gpu_mem_limit = 2048
        db_name_in = "detect.db"
        db_name_out = "track.db"
        unpacked_args = arg[0].split(";")
        for line in unpacked_args:
            key_value = line.split("=")
            if key_value[0] == "model_name":
                model_name = key_value[1]
            if key_value[0] == "gpu_mem_limit":
                gpu_mem_limit = int(key_value[1])
            if key_value[0] == "db_name_in":
                db_name_in = key_value[1]
            if key_value[0] == "db_name_out":
                db_name_out = key_value[1]
        print("model_name:", model_name, "gpu_mem_limit:", gpu_mem_limit, "db_name_in", db_name_in, "db_name_out", db_name_out)
        self.gpu_cfg(gpu_mem_limit)
        self.model = tf.saved_model.load(model_name)
        self.min_height = 0
        self.min_confidence = 0.3
        self.nms_max_overlap = 0.8
        self.image_shape = [128,64]
        max_cosine_distance = 0.2
        nn_budget = 100
        metric = NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
        self.tracker = Tracker(metric)

        self.db_in = storage.Detections(("db_name=" + db_name_in,))
        self.db_out = storage.Detections(("db_name=" + db_name_out,))
        print(sys.path[0], "Deep Sort initialized")


    def gpu_cfg(self, mem_lmt):
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=mem_lmt)])
            except RuntimeError as e:
                print(e)

    def extract_image_patch(self, image, bbox, patch_shape):
        bbox = np.array(bbox)
        if patch_shape is not None:
            # correct aspect ratio to patch shape
            target_aspect = float(patch_shape[1]) / patch_shape[0]
            new_width = target_aspect * bbox[3]
            bbox[0] -= (new_width - bbox[2]) / 2
            bbox[2] = new_width

        # convert to top left, bottom right
        bbox[2:] += bbox[:2]
        bbox = bbox.astype(int)

        # clip at image boundaries
        bbox[:2] = np.maximum(0, bbox[:2])
        bbox[2:] = np.minimum(np.asarray(image.shape[:2][::-1]) - 1, bbox[2:])
        if np.any(bbox[:2] >= bbox[2:]):
            return None
        sx, sy, ex, ey = bbox
        image = image[sy:ey, sx:ex]
        image = cv2.resize(image, tuple(patch_shape[::-1]))
        return image

    def __call__(self, arg):
        image = arg[0][0]
        rts = arg[2][0]
        tmp = self.db_in.get(rts)
        frame_detections = np.array(tmp)
        height = image.shape[0]
        width = image.shape[1]   
        frame_detections[:,(0, 2)] *= width
        frame_detections[:,(1, 3)] *= height

        patches = []
        for fd in frame_detections:
            fd_details = fd[0:4]
            patch = self.extract_image_patch(image, fd_details, self.image_shape)
            patches.append(patch)

        input = tf.convert_to_tensor(np.asarray(patches))
        output = self.model.signatures['serving_default'](input)

        detection_list = []
        for i in range(len(frame_detections)):
            feature = output['out'][i]
            frame_detection = frame_detections[i][0:4]
            confidence = frame_detections[i][4]
            detection_list.append(Detection(frame_detection, confidence, feature))

        detection_list = [d for d in detection_list if d.confidence >= self.min_confidence]
        boxes = np.array([d.tlwh for d in detection_list])
        scores = np.array([d.confidence for d in detection_list])
        indices = non_max_suppression(boxes, self.nms_max_overlap, scores)
        detection_list = [detection_list[i] for i in indices]

        self.tracker.predict()
        self.tracker.update(detection_list)

        results = []
        for track in self.tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            bbox = track.to_tlwh()
            results.append([track.track_id, bbox])
            cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), (int(bbox[0]+bbox[2]), int(bbox[1]+bbox[3])), (0, 255, 0), 1)
            cv2.putText(image, str(track.track_id), (int(bbox[0]), int(bbox[1])), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        count = -1
        for result in results:
            count += 1
            overlap = iou(result[1], frame_detections[:,[0,1,2,3]])
            max = np.amax(overlap)
            if (max > 0.6):
                res = np.where(overlap == np.amax(overlap))
                index = res[0]
                frame_detections[index[0]][6] = result[0]

        frame_detections[:,(0, 2)] /= width
        frame_detections[:,(1, 3)] /= height
        self.db_out.put(frame_detections)
        return image
