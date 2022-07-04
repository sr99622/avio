Installation
============

.. _installation_notes:

Installation Notes
------------------

It can be helpful to understand a bit about the inner workings of avio when
considering the path to installation.  Factors to consider when using avio 
include the platform and the desired level of control over the workings of 
the underlying libraries used by the system.  Paramount importance applies 
to FFMPEG.

Both of these libraries are quite complex, and include portions which may 
require user compilation if specific features are needed.  If GPU usage is
desired, FFMPEG will have to be compiled by the user for their configuration
on Linux platforms.  Additionally, some features of these libraries are what 
is termed non-free, in that it is not generally permitted to distribute 
precompiled binary versions of these libraries.

Compiling these libraries is an advanced exercise and will require skill and 
experience to be successful.  It is possible, however, to use precompiled 
binaries for these libraries, with the understanding that resulting system 
will have reduced functionality.

Furthermore, avio is largely a binary module.  This means that the binary
files used during compilation must match exactly the binary files used during 
runtime. This places some very restrictive requirements on the runtime 
environment if avio is installed as a precompiled binary.  If the underlying 
binary files, namely DLL's on windows, are changed for some reason, avio will 
not work unless it is recompiled to match the existing DLL versions.

For these reasons, avio has been designed to work with the Anaconda packaging
system.  It is not strictly required to use Anaconda, but it will make the 
chore of installing avio far simpler.  This will apply to both situations where
it is desired to compile from source, or use the precompiled configuration.

.. _using_conda:

Using Conda for Installation
----------------------------

This will only work on windows with python version 3.9.  Anaconda must be 
installed on the target machine.  First create a new environment and activate. 
Install avio from the channel

.. code-block:: text

    conda create --name test
    conda activate test
    conda install -c sr99622 avio

This will install avio and its dependencies, using python version 3.9.7.  To see 
if it was installed correctly, launch python, import avio and check version.

.. code-block:: text

    python
    import avio
    print(__avio__.version)

.. _compilation:

Compilation From Source
-----------------------

Compilation from source is a far superior method for installing the program
and will afford the maximum functionality.  It is the only way to employ 
GPU driven FFMPEG on linux.  In order to be succesful in the compilation, 
all of the required component libraries must have been previously installed.  
In some cases, it is possible that the component libraries may have precompiled 
binaries available.  The required component libraries are listed below:

.. code-block:: text

    FFMPEG
    SDL2_ttf
        SDL2
        freetype
        libpng
        zlib


In order to compile these libraries, a compiler must be installed on the 
host machine.  For windows, the compiler most often used is Visual Studio.  
This can be downloaded from https://visualstudio.microsoft.com/downloads/.  
Any version of Visual Studio that supports C++17 will work.  When installing 
Visual Studio, make sure to check the Desktop development with C++ tools.  

On Linux, the g++ compiler is needed.  This can be installed using apt.

.. code-block:: text

    sudo apt install g++

The downside of compilation from source is the difficulty of the process 
and the skill and experience required to be successful in the effort.  Of
the libraries shown above, FFMPEG is the most critical and the most 
difficult to compile.  SDL2_ttf has some dependencies of its own that 
require consideration when compiling, which can add complexity to
the task.

The recommended path for this exercise is to leverage the pre compiled
libraries found on conda forge as a starting point for the process.  This
will get avio up and running quickly, after which more exotic functionality
can be added to improve performance.  To learn more about conda forge, 
visit https://conda-forge.org/.

Conda forge has versions of these libraries which are precompiled and
easily installed.  It is possible to create an environment using conda
forge that will allow compilation of avio without additional resources.
To create a compilation environment the following command could be used.
It is recommended to add conda forge to your conda channels first, so
an environment can be added seamlessly.  In the example shown below,
the environment being added is named test.

.. code-block:: text

    conda config --add channels conda-forge
    conda create --name test python ffmpeg sdl2_ttf
    conda activate test

Now that the conda environment has been set up, the source code can be
downloaded from github using the following command.  Note the use of 
the recursive flag to get the pybind11 submodule, which is required.

.. code-block:: text
    
    git clone --recursive https://github.com/avio.git


Once the source code has been downloaded, the compilation and install
process follows.  The following commands are entered from the command
prompt while in the conda test environment built earlier.  The process
is identical for either windows or linux.

.. code-block:: text

    cd avio
    pip install .

Upon completion of this process, there will be a usable avio set up on 
the host machine.  There is a test program that can be used to verify
operation.  It is invoked as follows

.. code-block:: text

    cd python
    python test.py

The test program will read from the test.mp4 file and apply a simple 
video and audio filter then write the converted streams to a file
named output.mp4.  The output may be observed with ffplay

.. code-block:: text

    ffplay output.mp4

The abilities of the configuration will be constrained by the limitations 
of the pre compiled component libraries.  On windows, FFMPEG will have 
basic GPU functionality with CUDA enabled decoding and encoding.  For 
linux installations, FFMPEG will be restricted to CPU codecs only.

In order to acheive better performance, these libraries will need to
be compiled from scratch before inclusion with avio.  For FFMPEG compile
on windows, the excellent ShiftMediaProject is recommended.  Learn
more at https://github.com/ShiftMediaProject/FFmpeg.

.. _installation_errors:

Installation Errors
-------------------

Unfortunately, there may be times when the compilation process fails.  The 
nature of a system such as avio is very complex and there are a lot of 
variables that have to line up exactly in order for the system to work.

If the host machine has different versions of the underlying libraries, it
is possible that avio will have linked to one version during compilation, then
be unable to find that exact version during runtime.  A sympton of this type
of error is the message appearing when attempting to import avio in python

.. code-block:: text

    ImportError: DLL load failed while importing avio: The specified module could not be found.

This type of error is sometimes caused by a stale CMake cache.  Clearing the
build directory under the avio directory can sometimes clear up this error.

A tool which can be useful in finding the broken dependency on windows is
https://github.com/lucasg/Dependencies.  Use the command prompt in the conda
environment to launch the DependenciesGui program so that it is loaded with
the current environment variables.

There may also be issue with the audio sub system.  This may be more
likely to occur on linux, especially if the delevopment libraries for the
audio sub system are not present on the host machine.  The presents some
difficulty for the SDL module, which requires linking to the development
libraries for audio functionality on some cases.  Simply disabling the 
audio processing in avio is a quick way around this problem if audio
functions are not needed.  Properly configuring the host machine such
that SDL can link to the audio development libraries is a complex
process beyond the scope of this document.

