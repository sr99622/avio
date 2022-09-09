import os
import warnings
import cv2
import numpy as np
from queue import Queue
from argparse import ArgumentParser

from mmpose.apis import (inference_top_down_pose_model, init_pose_model,
                         process_mmdet_results, vis_pose_result)
from mmpose.datasets import DatasetInfo

try:
    from mmdet.apis import inference_detector, init_detector
    has_mmdet = True
except (ImportError, ModuleNotFoundError):
    has_mmdet = False

class Pose:
    def __init__(self, arg):
        print("Pose.__init__")
        det_config = "mmlab/configs/faster_rcnn/faster_rcnn_r50_fpn_coco.py"
        det_ckpt = "mmlab/checkpoints/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"
        pose_config = "mmlab/configs/body/2d_kpt_sview_rgb_vid/posewarper/posetrack18/hrnet_w48_posetrack18_384x288_posewarper_stage2.py"
        pose_ckpt = "mmlab/checkpoints/hrnet_w48_posetrack18_384x288_posewarper_stage2-4abf88db_20211130.pth"

        self.det_cat_id = 1
        self.use_multi_frames = True
        self.online = False

        self.det_model = init_detector(det_config, det_ckpt, device='cuda:0')
        self.pose_model = init_pose_model(pose_config, pose_ckpt, device='cuda:0')

        self.dataset = self.pose_model.cfg.data['test']['type']
        self.dataset_info = self.pose_model.cfg.data['test'].get('dataset_info', None)
        if self.dataset_info is None:
            warnings.warn('Please set dataset_info in the config')
        else:
            self.dataset_info = DatasetInfo(self.dataset_info)

        if self.use_multi_frames:
            assert 'frame_indices_test' in self.pose_model.cfg.data.test.data_cfg
            self.indices = self.pose_model.cfg.data.test.data_cfg['frame_indices_test']

        self.return_heatmap = False
        self.output_layer_names = None
        self.bbox_thr = 0.3
        self.kpt_thr = 0.3
        self.radius = 4
        self.thickness = 1
        self.frame_id = 0

    def __call__(self, arg):
        #print("Pose.__call")
        img = arg[0][0]
        self.frame_id += 1

        mmdet_results = inference_detector(self.det_model, img)
        person_results = process_mmdet_results(mmdet_results, self.det_cat_id)

        frames = []
        frames.append(img)
        frames.append(img)
        frames.append(img)
        frames.append(img)
        frames.append(img)
        self.frame_id += 1

        pose_results, returned_outputs = inference_top_down_pose_model(
            self.pose_model,
            frames,
            person_results,
            bbox_thr=self.bbox_thr,
            format='xyxy',
            dataset=self.dataset,
            dataset_info=self.dataset_info,
            return_heatmap=self.return_heatmap,
            outputs=self.output_layer_names)

        img = vis_pose_result(
            self.pose_model,
            img,
            pose_results,
            dataset=self.dataset,
            dataset_info=self.dataset_info,
            kpt_score_thr=self.kpt_thr,
            radius=self.radius,
            thickness=self.thickness,
            show=False)

        return img

if __name__ == "__main__":
    pose = Pose("ckpt_file=auto")
    img = cv2.imread("C:/Users/stephen/Pictures/test.jpg")
    img = pose(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)
