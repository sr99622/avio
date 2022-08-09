avio
====

Full documentation is available at [Read the Docs](https://avio.readthedocs.io/en/latest/)

**avio** is a Python package for processing multimedia files and streams.  It it built upon the 
foundation of FFMPEG, but it is not a thin wrapper.  The details of using FFMPEG have been 
abstracted away and modularized so that the developer may focus on higher level operations 
without being concerned with the details of the underlying mechanics.

Display of the video and audio streams is provided automatically, and a minimal in-screen 
GUI is available by default for basic operations including pause, seek and single step 
operations in both forward and reverse time order.  The GUI may be supplanted by the 
developer for more sophisticated operations if desired.

The package provides a callback mechanism by which the video stream frames may be manipulated
using a python interface.  This is a powerful feature that allows developers to work on 
individual frames as they are processed through the system using python functions, operations 
that previously would have required a C++ interface to implement.

In addition to GPU image processisng, full access to hardware GPU decoding and encoding is 
possible, harnessing the power of the GPU to improve perfomance during read and write operations. 
Most common formats are easily configured, allowing the devloper to present data to a wider
audience.

Installation Quick Start
-------------------

Anaconda must be installed on the host machine.  The download is available at
https://www.anaconda.com/products/distribution

Using the anaconda prompt, create a new conda environment with avio and activate it, 
as shown below.  Windows users may consult this link for further reference
[[Anaconda prompt on Windows]](https://docs.anaconda.com/anaconda/user-guide/getting-started/#open-anaconda-prompt).
For linux users, the terminal should start automatically in the Anaconda environment.

The Anaconda prompt will start in the users home directory.  This location is important
because it is the starting point for the installation.  To return to the user home
directory, use the environment variable. for windows, this is ```cd %HOMEPATH% ``` or on linux
the command to return to the user home directory is ```cd $HOME```

Installing avio
---------------

Add the conda forge channel to the conda configuration

```bash
conda config --add channels conda-forge
```

Create environment for avio and activate it

```bash
conda create --name myenv -c sr99622 avio
conda activate myenv
```

Download the source code and example programs

```bash
git clone --recursive https://github.com/sr99622/avio.git
```

The avio source code comes with a small test file that can be used to verify
the operation of the program.

```bash
cd avio/python
python play.py test.mp4
```

Installing ByteTrack
--------------------

The ByteTrack and YOLOX module can be added for detection and tracking.  It is 
suggested to use mamba to speed up this install.  Install pytorch first.

```bash
conda install mamba
mamba install pytorch torchvision torchaudio cudatoolkit=11.6 -c pytorch -c nvidia
mamba install -c sr99622 yolox
```

A pretrained model is available for downloading to test the program.  The model
will download automatically the first time the program is run.  Use the 
following command.

```bash
python play.py test.mp4 --vfilter format=bgr24 --bytetrack ckpt_file=auto
```

The ckpt_file=auto directive will tell the program to download the medium version
of the bytetrack model and use that to implement tracking.  The auto download will
place the file in the users home directory under ~/.cache/torch/hub/checkpoints

It is possible to improve model performance using fp16 math on the gpu.  The 
following command shows an example

```bash
python play.py test.mp4 --vfilter format=bgr24 --bytetrack ckpt_file=auto,fp16=True
```

Installing TensorRT
-------------------

The model runtime performance can be improved dramatically using TensorRT, which may be installed
as shown below

On Linux:

```bash
cd $HOME
pip install nvidia-pyindex
pip install nvidia-tensorrt
export CUDA_HOME=$CONDA_PREFIX
git clone https://github.com/NVIDIA-AI-IOT/torch2trt.git
cd torch2trt
pip install .
cd $HOME/avio/python

```

On Windows:

Go to https://developer.nvidia.com/tensorrt and download the zip file using your
NVIDIA credentials.  Unzip the file in a local directory.

```bash
cd %HOMEPATH%
unzip TensorRT-x.x.x.x.Windows....
cd TensorRT-x.x.x.x.Windows.......   #(the unzipped directory)
cd TensorRT-x.x.x.x                  #(the content directory e.g. TensorRT-8.4.1.5)
copy lib\*.dll %CONDA_PREFIX%\Library\bin
copy lib\*.lib %CONDA_PREFIX%\Library\lib
copy include\* %CONDA_PREFIX%\Library\include
set CUDA_HOME=%CONDA_PREFIX%
cd python
pip install tensorrt-8.4.1.5-cp39-none-win_amd64.whl
mamba install cudnn -y
git clone https://github.com/NVIDIA-AI-IOT/torch2trt.git
cd torch2trt
pip install .
cd %HOMEPATH%\avio\python

```

TensorRT creates an optimized version of the model based on the characteristics
of the specific GPU installed on the local machine.  The following command
will create the TensorRT version of the model and run it.  The model will take several 
minutes to build and will produce some warning messages which can safely be ignored.
Once the model has been created, the program will launch.

```bash
python play.py test.mp4 --vfilter format=bgr24 --bytetrack trt_file=auto 
```

Installing detectron2
---------------------

Download the source code and compile.  This repository has been modified from the 
original detectron2 to disable extensions.


```bash
git clone https://github.com/sr99622/detectron2.git
cd detectron2
pip install .
```

Detection, yeypoint and instance segmentation models are available for detectron2
using the folowing commands

```bash
python play.py test.mp4 --vfilter format=bgr24 --detection ckpt_file=auto
python play.py test.mp4 --vfilter format=bgr24 --keypoint ckpt_file=auto
python play.py test.mp4 --vfilter format=bgr24 --segment ckpt_file=auto
```

Credits
-------



ByteTrack is borrowed from https://github.com/ifzhang/ByteTrack

YOLOX is borrowed from https://github.com/Megvii-BaseDetection/YOLOX

detectron2 is borrowed from https://github.com/facebookresearch/detectron2


-----------------------------------------------

## Cite ByteTrack

```
@article{zhang2022bytetrack,
  title={ByteTrack: Multi-Object Tracking by Associating Every Detection Box},
  author={Zhang, Yifu and Sun, Peize and Jiang, Yi and Yu, Dongdong and Weng, Fucheng and Yuan, Zehuan and Luo, Ping and Liu, Wenyu and Wang, Xinggang},
  booktitle={Proceedings of the European Conference on Computer Vision (ECCV)},
  year={2022}
}
```

## Acknowledgement

A large part of the code is borrowed from [YOLOX](https://github.com/Megvii-BaseDetection/YOLOX), [FairMOT](https://github.com/ifzhang/FairMOT), [TransTrack](https://github.com/PeizeSun/TransTrack) and [JDE-Cpp](https://github.com/samylee/Towards-Realtime-MOT-Cpp). Many thanks for their wonderful works.

## License

[LICENSE](https://github.com/ifzhang/ByteTrack/blob/main/LICENSE)

----------------------------------------------

## Cite YOLOX
If you use YOLOX in your research, please cite our work by using the following BibTeX entry:

```latex
 @article{yolox2021,
  title={YOLOX: Exceeding YOLO Series in 2021},
  author={Ge, Zheng and Liu, Songtao and Wang, Feng and Li, Zeming and Sun, Jian},
  journal={arXiv preprint arXiv:2107.08430},
  year={2021}
}
```
## In memory of Dr. Jian Sun
Without the guidance of [Dr. Sun Jian](http://www.jiansun.org/), YOLOX would not have been released and open sourced to the community.
The passing away of Dr. Sun Jian is a great loss to the Computer Vision field. We have added this section here to express our remembrance and condolences to our captain Dr. Sun.
It is hoped that every AI practitioner in the world will stick to the concept of "continuous innovation to expand cognitive boundaries, and extraordinary technology to achieve product value" and move forward all the way.

<div align="center"><img src="assets/sunjian.png" width="200"></div>
没有孙剑博士的指导，YOLOX也不会问世并开源给社区使用。
孙剑博士的离去是CV领域的一大损失，我们在此特别添加了这个部分来表达对我们的“船长”孙老师的纪念和哀思。
希望世界上的每个AI从业者秉持着“持续创新拓展认知边界，非凡科技成就产品价值”的观念，一路向前。

## License

[LICENSE](https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE)

-------------------------------------------------

## Citing Detectron2

If you use Detectron2 in your research or wish to refer to the baseline results published in the [Model Zoo](MODEL_ZOO.md), please use the following BibTeX entry.

```BibTeX
@misc{wu2019detectron2,
  author =       {Yuxin Wu and Alexander Kirillov and Francisco Massa and
                  Wan-Yen Lo and Ross Girshick},
  title =        {Detectron2},
  howpublished = {\url{https://github.com/facebookresearch/detectron2}},
  year =         {2019}
}
```
## License

[LICENSE](https://github.com/facebookresearch/detectron2/blob/main/LICENSE)

-------------------------------------------------
