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
suggested to use mamba to speed up this install

```bash
conda install mamba
mamba install -c sr99622 -c pytorch yolox
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

Credits
-------

ByteTrack is borrowed from https://github.com/ifzhang/ByteTrack

YOLOX is borrowed from https://github.com/Megvii-BaseDetection/YOLOX

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
