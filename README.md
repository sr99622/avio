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

Anaconda should be installed on the host machine.  The download is available at
https://www.anaconda.com/products/distribution

Add the conda forge channel to the conda configuration

```bash
conda config --add channels conda-forge
```

Using the anaconda prompt, create a new conda environment with avio and activate it, 
as shown below.  Windows users may consult this link for further reference
[[Anaconda prompt on Windows]](https://docs.anaconda.com/anaconda/user-guide/getting-started/#open-anaconda-prompt)

```bash
conda create --name test -c sr99622 avio
conda activate test
```

Download the source code and example programs

```bash
git clone --recursive https://github.com/sr99622/avio.git
```

The avio source code comes with a small test file that you can use to verify
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

A pretrained model is available for downloading to test the program.  You can do
this automatically using the following command.  This assumes you are still in the
avio\python directory as shown above.

```bash
python play.py test.mp4 --vfilter format=bgr24 --bytetrack "ckpt_file=auto"
```

The ckpt_file=auto directive will tell the program to download the medium version
of the bytetrack model and use that to implement tracking.  Other sizes and 
variations of the bytetrack model are available from the [ByteTrack homepage] https://github.com/ifzhang/ByteTrack#model-zoo

These models can be downloaded and placed on the local machine.  The ckpt_file=
directive can be used to tell the program where to find the model.  Note that 
the large and medium models are the only ones fully implemented here, other models
will require adjustment to the bytetrack/interface.py file and installation of the
appropriate file from ByteTrack/exps/example/mot to the avio/python/bytetrack folder.

It is possible to improve model performance using fp16 math on the gpu.  The 
following command shows an example

```bash
python play.py test.mp4 --vfilter format=bgr24 --bytetrack "ckpt_file=auto;fp16=True"
```

Installing TensorRT
-------------------

The model runtime can be improved dramatically using TensorRT.  To install TensorRT

On Linux:

```bash
pip install nvidia-pyindex
pip install nvidia-tensorrt
export CUDA_HOME=$CONDA_PREFIX
git clone https://github.com/NVIDIA-AI-IOT/torch2trt.git
cd torch2trt
pip install .
```

On Windows:

Go to https://developer.nvidia.com/tensorrt and download the zip file using your
NVIDIA credentials.  Unzip the file in a local directory.

```bash
cd TensorRT-x.x.x.x.Windows.......   #(the unzipped directory)
cd TensorRT-x.x.x.x                  #(the content directory e.g. TensorRT-8.4.1.5)
copy lib\*.dll %CONDA_PREFIX%\Library\bin
copy lib\*.lib %CONDA_PREFIX%\Library\lib
copy include\* %CONDA_PREFIX%\Library\include
set CUDA_HOME=%CONDA_PREFIX%
cd python
pip install tensorrt-8.4.1.5-cpXX-none-win_amd64.whl  #(XX is your conda environment python version, should be 39)
mamba install cudnn
git clone https://github.com/NVIDIA-AI-IOT/torch2trt.git
cd torch2trt
pip install .
```

You now need to create the TensorRT version of the model for your specific GPU.
TensorRT creates an optimized version of the model based on the characteristics
of the specific GPU installed on the local machine.

```bash
cd to your avio installation directory
cd avio/python
python bytetrack/trt.py -f bytetrack/yolox_m_mix_det.py -c /path/to/model/bytetrack_m_mot17.pth.tar
```

The TensorRT version of the model will be installed adjacent to the torch version
/path/to/model/bytetrack_m_mot17_trt.pth

To run the optimized TensorRT model use the command

```bash
python play.py test.mp4 --vfilter format=bgr24 --bytetrack "trt_file=/path/to/model/bytetrack_m_mot17_trt.pth"
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