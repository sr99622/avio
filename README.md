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
https://docs.anaconda.com/anaconda/user-guide/getting-started/#open-anaconda-prompt

```bash
conda create --name test -c sr99622 avio
conda activate test
```

Download the source code and example programs

```bash
git clone --recursive https://github.com/sr99622/avio.git
```

Run the sample test program

```bash
cd avio\python
python test.py
```

The ByteTrack and YOLOX module can be added for detection and tracking.  It is 
suggested to use mamba to speed up this install

```bash
conda install mamba
mamba install -c sr99622 -c pytorch yolox
```

You can get the pretrained model (bytetrack_l_mot17.pth.tar) for this at 
https://drive.google.com/file/d/1XwfUuCBF4IgWBWK2H7oOhQgEj9Mrb3rz/view?usp=sharing
You will need to adjust the code in avio\python\bytetrack\interface.py to point to 
the location of the model on the local machine.

The model runtime can be improved dramatically using TensorRT.  To install TensorRT

On Linux:

```bash
pip install nvidia-pyindex
pip install nvidia-tensorrt
git clone https://github.com/NVIDIA-AI-IOT/torch2trt.git
cd torc2trt
pip install .
```

On Windows:
Go to https://developer.nvidia.com/tensorrt and download the zip file using your
NVIDIA credentials.  Unzip the file in a local directory.

```bash
cd TensorRT-x.x.x.x.Windows.......   (the unzipped directory)
cd TensorRT-x.x.x.x                  (the content directory e.g. TensorRT-8.4.1.5)
copy lib\*.dll %CONDA_PREFIX%\Library\bin
copy lib\*.lib %CONDA_PREFIX%\Library\lib
copy include\* %CONDA_PREFIX%\Library\include
set CUDA_HOME=%CONDA_PREFIX%
cd ..\python
pip install tensorrt-8.4.1.5-cpXX-none-win_amd64.whl  (XX is your conda environment python version, should be 39)
```

You now need to create the TensorRT version of the model for your specific GPU

```bash
cd to your avio installation directory
cd avio/python
python bytetrack/trt.py -f bytetrack/yolox_l_mix_det.py -c /path/to/model/bytetrack_l_mot17.pth.tar
```

The TensorRT version of the model will be installed adjacent to the torch version
/path/to/model/bytetrack_l_mot17_trt.pth

You will need to adjust the parameter in the avio/python/bytetrack/interface.py file to match your local
configuration.
