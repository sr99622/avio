avio
====

**avio** is a Python package for processing multimedia files and streams.  It it built upon the 
foundation of FFMPEG, but it is not a thin wrapper.  The details of using FFMPEG have been 
abstracted away and modularized so that the developer may focus on higher level operations 
without being concerned with the details of the underlying mechanics.  OpenCV is integrated 
into the package as well, so that commonly used functions and formats are readily available 
without further configuration.  

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

Windows Quick Start
-------------------

The following instructions are for windows users.  

Anaconda should be installed on the host machine.  The download is available at
https://www.anaconda.com/products/distribution#windows.

Using the anaconda prompt, as shown in this link 
https://docs.anaconda.com/anaconda/user-guide/getting-started/#open-anaconda-prompt
create a new conda environment and activate it, as shown below.

```bash
conda create --name test
conda activate test
```

Add the conda forge channel to the conda configuration

```bash
conda config --add channels conda-forge
```

Install avio

```bash
conda install -c sr99622 avio
```

Download the source code and example programs

```bash
git clone --recursive https://github.com/sr99622/avio.git
```

Run the sample test program

```bash
cd avio\\python
python test.py
```