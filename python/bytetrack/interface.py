import argparse
import os
import os.path as osp
import time
import cv2
import torch
import numpy as np

from loguru import logger

from yolox.data.data_augment import preproc
from yolox.exp import get_exp
from yolox.utils import fuse_model, get_model_info, postprocess
from yolox.utils.visualize import plot_tracking
from yolox.tracker.byte_tracker import BYTETracker
from yolox.tracking_utils.timer import Timer

from torchvision.transforms import functional

#'''
class Predictor(object):
    def __init__(
        self,
        model,
        exp,
        trt_file=None,
        decoder=None,
        device=torch.device("cuda"),
        fp16=False
    ):
        self.model = model
        self.decoder = decoder
        self.num_classes = exp.num_classes
        self.confthre = exp.test_conf
        self.nmsthre = exp.nmsthre
        self.test_size = exp.test_size
        self.device = device
        self.fp16 = fp16
        if trt_file is not None:
            from torch2trt import TRTModule

            model_trt = TRTModule()
            model_trt.load_state_dict(torch.load(trt_file))

            x = torch.ones((1, 3, exp.test_size[0], exp.test_size[1]), device=device)
            self.model(x)
            self.model = model_trt
        self.rgb_means = (0.485, 0.456, 0.406)
        self.std = (0.229, 0.224, 0.225)
        #self.timer = Timer()

    def inference(self, img, timer):
        #timer.tic()
        img_info = {"id": 0}
        if isinstance(img, str):
            img_info["file_name"] = osp.basename(img)
            img = cv2.imread(img)
        else:
            img_info["file_name"] = None

        height, width = img.shape[:2]
        img_info["height"] = height
        img_info["width"] = width
        img_info["raw_img"] = img

        ratio = min(self.test_size[0] / img.shape[0], self.test_size[1] / img.shape[1])
        img_info["ratio"] = ratio
        inf_shape = (int(img.shape[0] * ratio), int(img.shape[1] * ratio))
        bottom = self.test_size[0] - inf_shape[0]
        side = self.test_size[1] - inf_shape[1]
        pad = (0, 0, side, bottom)

        img = functional.to_tensor(img.copy()).to(self.device)
        img = functional.resize(img, inf_shape)
        img = functional.pad(img, pad, 0.447)
        img = functional.normalize(img, self.rgb_means, self.std, True)
        img = img.unsqueeze(0)

        if self.fp16:
            img = img.half()  # to FP16

        with torch.no_grad():
            outputs = self.model(img)
            if self.decoder is not None:
                outputs = self.decoder(outputs, dtype=outputs.type())
            outputs = postprocess(
                outputs, self.num_classes, self.confthre, self.nmsthre
            )
            #logger.info("Infer time: {:.4f}s".format(time.time() - t0))

        #timer.toc()
        return outputs, img_info
#'''

class Argument:
    track_thresh = 0.5
    track_buffer = 30
    mot20 = False
    match_thresh = 0.8
    aspect_ratio_thresh = 1.6
    min_box_area = 10.0
    #ckpt = "/home/stephen/source/ByteTrack/pretrained/bytetrack_l_mot17.pth.tar"
    #ckpt = "/home/stephen/Downloads/yolox_l.pth"
    ckpt = "C:/users/sr996/source/repos/ByteTrack/pretrained/bytetrack_l_mot17.pth.tar"
    trt = True
    fp16 = False
    #trt_file = "/home/stephen/source/ByteTrack/YOLOX_outputs/yolox_l_mix_det/model_trt.pth"
    #trt_file = "C:/users/sr996/source/repos/ByteTrack/YOLOX_outputs/yolox_l_mix_det/model_trt.pth"
    trt_file = "C:/Users/sr996/source/pretrained/bytetrack_l_mot17_trt.pth"

class ByteTrack:
    def __init__(self):
        print("ByteTrack.__init__")

        #'''
        try :
            self.args = Argument()
            print(self.args.mot20)
            self.exp = get_exp("yolox_l_mix_det.py", None)
            print("exp.name", self.exp.exp_name)
            device = torch.device("cuda")
            model = self.exp.get_model().to(device)
            #logger.info("Model Summary: {}".format(get_model_info(model, self.exp.test_size)))
            model.eval()

            if self.args.trt: 
                print("loading TensorRT model: ", self.args.trt_file)
                model.head.decode_in_inference = False
                decoder = model.head.decode_outputs
                trt_file = self.args.trt_file
            else:
                ckpt_file = self.args.ckpt
                logger.info("loading checkpoint: {}", ckpt_file)
                ckpt = torch.load(ckpt_file, map_location="cpu")
                model.load_state_dict(ckpt["model"])
                logger.info("Loaded checkpoint success")
                decoder = None
                trt_file = None

                if self.args.fp16:
                    model = model.half()

            self.predictor = Predictor(model, self.exp, trt_file, decoder, device, self.args.fp16)
            self.tracker = BYTETracker(self.args)
            self.timer = Timer()
            self.frame_id = 0
            print("init complete")
        except BaseException as err:
            #print(f"Unexpected {err=}, {type(err)=}")
            logger.exception("ByteTrack initialization failure")
            raise
        #'''

    def __call__(self, arg):
        #print("ByteTrack.__call__")

        #'''
        try :
            self.timer.tic()

            img = arg[0][0]
            rts = arg[2][0]
            #print(rts)
            #print("image shape", img.shape)
            outputs, img_info = self.predictor.inference(img, self.timer)
            #print(outputs)
            if outputs[0] is not None:
                #print(outputs[0].shape)
                online_targets = self.tracker.update(outputs[0], [img_info['height'], img_info['width']], self.exp.test_size)
                online_tlwhs = []
                online_ids = []
                online_scores = []
                for t in online_targets:
                    tlwh = t.tlwh
                    tid = t.track_id
                    vertical = tlwh[2] / tlwh[3] > self.args.aspect_ratio_thresh
                    if tlwh[2] * tlwh[3] > self.args.min_box_area and not vertical:
                        online_tlwhs.append(tlwh)
                        online_ids.append(tid)
                        online_scores.append(t.score)
                    
                self.timer.toc()
                online_im = plot_tracking(
                    img_info['raw_img'], online_tlwhs, online_ids, frame_id = self.frame_id + 1, fps=1. / self.timer.average_time
                )
            else:
                print('no return')
                self.timer.toc()
                online_im = img_info['raw_img']
            
            self.frame_id += 1


            return online_im       # return a modified image

        except BaseException as err:
            #print(f"Unexpected {err=}, {type(err)=}")
            logger.exception("ByteTrack runtime error")
            raise
        #'''

        #return pts       # return a modified pts
        #return False     # record trigger argument

        #return (img, pts, False)
        #return (img, pts)
        #return (img, False)
