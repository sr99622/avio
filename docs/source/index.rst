.. avio documentation master file, created by
   sphinx-quickstart on Sun May 22 13:25:00 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

avio
====

Python package for processing multimedia files and streams.  It it built upon the 
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

.. toctree::
   quickstart
   onscreen
   installation
   application
   howto
   callback
   objects
   sample
   :maxdepth: 2
   :caption: Contents:


