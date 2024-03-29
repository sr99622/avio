from loguru import logger

import tensorrt as trt
import torch
from torch2trt import torch2trt

from yolox.exp import get_exp

import argparse
import os
import shutil


def make_parser():
    parser = argparse.ArgumentParser("YOLOX ncnn deploy")
    parser.add_argument("-expn", "--experiment-name", type=str, default=None)
    parser.add_argument("-n", "--name", type=str, default=None, help="model name")

    parser.add_argument(
        "-f",
        "--exp_file",
        default=None,
        type=str,
        help="pls input your expriment description file",
    )
    parser.add_argument("-c", "--ckpt", default=None, type=str, help="ckpt path")
    return parser


def main():
    args = make_parser().parse_args()
    convert(args.exp_file, args.ckpt)


@logger.catch
def convert(exp_file, ckpt_file):
    exp = get_exp(exp_file, None)
    model = exp.get_model()

    ckpt = torch.load(ckpt_file, map_location="cpu")
   
    parts = os.path.split(ckpt_file)
    base = parts[0]
    name = parts[1]
    root = os.path.splitext(name)
    while root[1] != '':
        root = os.path.splitext(root[0])
    file_name = os.path.join(base, root[0] + "_trt.pth")
    engine_file = os.path.join(base, root[0] + "_trt.engine")

    model.load_state_dict(ckpt["model"])
    logger.info("loaded checkpoint done.")
    model.eval()
    model.cuda()
    model.head.decode_in_inference = False
    print("exp.test_size[0]", exp.test_size[0])
    print("exp.test_size[1]", exp.test_size[1])
    x = torch.ones(1, 3, exp.test_size[0], exp.test_size[1]).cuda()
    model_trt = torch2trt(
        model,
        [x],
        fp16_mode=True,
        log_level=trt.Logger.INFO,
        max_workspace_size=(1 << 32),
    )

    torch.save(model_trt.state_dict(), file_name)
    logger.info("Converted TensorRT model done.")

    with open(engine_file, "wb") as f:
        f.write(model_trt.engine.serialize())

    logger.info("Converted TensorRT model engine file is saved for C++ inference.")


if __name__ == "__main__":
    main()
