import cv2
import torch
import os
import numpy as np
from pathlib import Path
from sys import platform
from loguru import logger

from yolox.exp import get_exp
from yolox.utils import postprocess
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
        device=None,
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

            x = torch.ones((1, 3, exp.test_size[0], exp.test_size[1]), device=self.device)
            self.model(x)
            self.model = model_trt
        self.rgb_means = (0.485, 0.456, 0.406)
        self.std = (0.229, 0.224, 0.225)

    def inference(self, img):
        ratio = min(self.test_size[0] / img.shape[0], self.test_size[1] / img.shape[1])
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

        return outputs

class Argument:
    track_thresh = 0.5
    track_buffer = 30
    mot20 = False
    match_thresh = 0.8
    aspect_ratio_thresh = 1.6
    min_box_area = 10.0

def get_auto_ckpt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/bytetrack_m_mot17.pth.tar"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/bytetrack_m_mot17.pth.tar"
    return filename

def get_auto_trt_filename():
    filename = None
    if platform == "win32":
        filename = os.environ['HOMEPATH'] + "/.cache/torch/hub/checkpoints/bytetrack_m_mot17_trt.pth"
    elif platform == "linux":
        filename = os.environ['HOME'] + "/.cache/torch/hub/checkpoints/bytetrack_m_mot17_trt.pth"
    return filename

#'''
class ByteTrack:
    def __init__(self, arg):
        print("ByteTrack.__init__")
        #'''
        ckpt_file = None
        fp16 = False
        trt_file = None
        trt = False
        force_cpu = False

        unpacked_args = arg[0].split(",")
        for line in unpacked_args:
            key_value = line.split("=")
            print("key  ", key_value[0])
            print("value", key_value[1])
            if key_value[0] == "ckpt_file":
                ckpt_file = key_value[1]
            if key_value[0] == "fp16":
                fp16 = key_value[1].lower() == "true"
            if key_value[0] == "trt_file":
                trt_file = key_value[1]
                trt = True
            if key_value[0] == "force_cpu":
                force_cpu = key_value[1].lower() == "true"

        print("class ByteTrack initialized with the values from command line")
        print("ckpt_file", ckpt_file)
        print("trt_file", trt_file)
        print("trt", trt)
        print("fp16", fp16)
        print("force_cpu", force_cpu)

        try :
            if ckpt_file is not None:
                if ckpt_file.lower() == "auto":
                    ckpt_file = get_auto_ckpt_filename()
                    print("cpkt_file:", ckpt_file)
                    cache = Path(ckpt_file)

                    if not cache.is_file():
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        torch.hub.download_url_to_file("https://sourceforge.net/projects/avio/files/bytetrack_m_mot17.pth.tar/download", ckpt_file)

            elif trt_file is not None:
                if trt_file.lower() == "auto":
                    trt_file = get_auto_trt_filename()
                    cache = Path(trt_file)

                    if not cache.is_file():
                        source = get_auto_ckpt_filename()
                        from trt import convert
                        convert("bytetrack/yolox_m_mix_det.py", source)

            self.args = Argument()

            if trt_file is not None:
                if "_l_" in trt_file:
                    self.exp = get_exp("yolox_l_mix_det.py", None)
                else:
                    if "_m_" in trt_file:
                        self.exp = get_exp("yolox_m_mix_det.py", None)
            if ckpt_file is not None:
                if "_l_" in ckpt_file:
                    self.exp = get_exp("yolox_l_mix_det.py", None)
                else:
                    if "_m_" in ckpt_file:
                        self.exp = get_exp("yolox_m_mix_det.py", None)
            
            device_name = "cpu"
            if not force_cpu:
                if torch.cuda.is_available():
                    device_name = "cuda"
            device = torch.device(device_name)

            model = self.exp.get_model().to(device)
            model.eval()

            if trt: 
                print("loading TensorRT model: ", trt_file)
                model.head.decode_in_inference = False
                decoder = model.head.decode_outputs
            else:
                logger.info("loading checkpoint: {}", ckpt_file)
                ckpt = torch.load(ckpt_file, map_location="cpu")
                model.load_state_dict(ckpt["model"])
                logger.info("Loaded checkpoint success")
                decoder = None
                trt_file = None

                if fp16:
                    model = model.half()

            self.predictor = Predictor(model, self.exp, trt_file, decoder, device, fp16)
            self.tracker = BYTETracker(self.args)
            self.timer = Timer()
            self.frame_id = 0
            print("init complete")
        except BaseException as err:
            logger.exception("ByteTrack initialization failure")
            raise
        #'''

    def __call__(self, arg):
        #print("call")
        #'''
        try :
            orig_img = arg[0][0]
            img = np.ascontiguousarray(np.copy(orig_img))
            outputs = self.predictor.inference(img)
            if outputs[0] is not None:
                online_targets = self.tracker.update(outputs[0], [img.shape[0], img.shape[1]], self.exp.test_size)

                for t in online_targets:
                    tlwh = t.tlwh
                    tid = t.track_id
                    horizontal = tlwh[2] / tlwh[3] > self.args.aspect_ratio_thresh
                    if tlwh[2] * tlwh[3] > self.args.min_box_area and not horizontal:
                        x, y, w, h = tlwh
                        box = tuple(map(int, (x, y, x + w, y + h)))
                        id = int(tid)
                        id_text = '{}'.format(int(id))
                        color = ((37 * id) % 255, (17 * id) % 255, (29 * id) % 255)
                        cv2.rectangle(img, box[0:2], box[2:4], color, 2)
                        cv2.putText(img, id_text, (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

                    if id == 31 or id == 150:
                        x1, y1, x2, y2 = box
                        y1 = max(y1, 0)
                        x1 = max(x1, 0)
                        y2 = min(y2, img.shape[0])
                        x2 = min(x2, img.shape[1])
                        crop = orig_img[y1:y2, x1:x2]

                        dh = 512
                        dw = 256

                        blank = np.zeros((dh, dw, 3), dtype=np.uint8)

                        w = x2 - x1
                        h = y2 - y1
                        if h / w > 2:
                            scale = dh / h
                        else:
                            scale = dw / w
                        
                        h = int(h * scale)
                        w = int(w * scale)

                        resized = cv2.resize(crop, (w, h), interpolation=cv2.INTER_AREA)
                        blank[:h,0 :w, :] = resized
                        cv2.imshow('img', blank)
                        #cv2.imshow('img', resized)

            return img

        except BaseException as err:
            logger.exception("ByteTrack runtime error")
            raise
        #'''
