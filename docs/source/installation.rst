Installation
============

.. _installation_notes:

Installation Notes
------------------

It can be helpful to understand a bit about the inner workings of avio when
considering the path to installation.  Factors to consider when using avio 
include the platform and the desired level of control over the workings of 
the underlying libraries used by the system.  Paramount importance applies 
to the two major components, OpenCV and FFMPEG.

Both of these libraries are quite complex, and include portions which may 
require user compilation if specific features are needed.  If GPU usage is
desired, OpenCV will have to be compiled by the user for their configuration.
The same will hold true for FFMPEG on Linux platforms.  Additionally, some
features of these libraries are what is termed non-free, in that it is not
generally permitted to distribute precompiled binary versions of these 
libraries.

Compiling either of these libraries is an advanced exercise and will require
skill and experience to be successful.  It is possible, however, to use pre
compiled binaries for these libraries, with the understanding that resulting
system will have reduced functionality.

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
GPU functions in OpenCV, and for GPU driven FFMPEG on linux.  In order to be 
succesful in the compilation, all of the required component libraries must
have been previously installed.  In some cases, it is possible that the 
component libraries may have precompiled binaries available.  The required
component libraries are listed below:

.. code-block:: text

    OpenCV
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
the libraries shown above, OpenCV and FFMPEG are the most critical and the
most difficult to compile.  SDL2_ttf has some dependencies of its own
that require consideration when compiling, which can add complexity to
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
    conda create --name test python opencv ffmpeg sdl2_ttf
    conda activate test

Now that the conda environment has been set up, the source code can be
downloaded from github using the following command.  Note the use of 
the recursive flag to get the pybind11 submodule, which is required.

.. code-block:: text
    
    git clone --recursive https://github.com/avio.git


Once the source code has been dowmloaded, the compilation and install
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
of the pre compiled component libraries.  OpenCV will not have GPU 
capabilities.  On windows, FFMPEG will have basic GPU functionality with 
CUDA enabled decoding and encoding.  For linux installations, FFMPEG will 
be restricted to CPU codecs only.

In order to acheive better performance, these libraries will need to
be compiled from scratch before inclusion with avio.  Included below
are some notes for compiling OpenCV on windows.  For FFMPEG compile
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
https://github.com/lucasg/Dependencies.


Careful observation of the environment variables on the host machine may
reveal unexpected dependencies as well.  This will be most relevant if
there are multple versions of OpenCV on the host machine and the 
OpenCV_DIR environment variable is set, which will cause cmake to link
to that version of OpenCV, which may not be compatible with the OpenCV
version present in the conda environment.

The same will hold true for multiple FFMPEG versions on the host machine.

There may also be issue with the audio sub system.  This may be more
likely to occur on linux, especially if the delevopment libraries for the
audio sub system are not present on the host machine.  The presents some
difficulty for the SDL module, which requires linking to the development
libraries for audio functionality on some cases.  Simply disabling the 
audio processing in avio is a quick way around this problem if audio
functions are not needed.  Properly configuring the host machine such
that SDL can link to the audio development libraries is a complex
process beyond the scope of this document.

.. _compile_opencv_windows_gpu:

Compiling OpenCV on Windows with GPU
------------------------------------

avio is dependent upon OpenCV.  The easiest way to satisfy the OpenCV 
requirement is to use the standard version of OpenCV that is installed 
by either pip or conda, however, this approach will leave out GPU support 
for OpenCV, resulting in dismal performance.  In order to support GPU, 
OpenCV must be compiled from source.

This is a difficult task on Windows.  There are several resources online 
that can help with the chore, and are a good starting point when beginning 
the process.  Following are some overview notes to help narrow down the 
steps required for a successful build.

Both the opencv and opencv_contrib are required.  The CMake GUI is used to 
set the build variables.  The following options should be checked to enable 
the GPU support.  The NVidia GPU Computing Toolkit is required, as well as 
the proper cudnn dll.  Proper version matching will contribute to success.  
It will be necssary to configure the CMake variables several times during the
process, as some variables are dependent on other previously set variables,
and will not appear until the previous variables have been set and configured.

.. code-block:: text

    OPENCV_EXTRA_MODULES_PATH  path_to_opencv_contrib/modules
    WITH_CUDA
    OPENCV_DNN_CUDA
    CUDA_FAST_MATH
    CUDA_ARCH_BIN  according to the GPU compute capability

The python module is the goal of the exercise, so the python parameters must
be properly set as well.

.. code-block:: text

    OPENCV_PYTHON3_VERSION

This variable when checked will enabled the build for the python module.  It
should trigger some accompanying variables when configured.  The CMake
system will in most cases find the important locations of python libraries 
and include directories with the exception of numpy.

.. code-block:: text

    PYTHON3_NUMPY_INCLUDE_DIRS 

This variable will most likely need to be set manually.  This 
can take some effort to find.  The PYTHON3_PACKAGES_PATH in a conda 
environment will hold a numpy directory under which there should be a 
core/include subdirectory which is the location required. Note that 
the python module will not be built without this setting.

Tests should be disabled, as they are not necessary and have a tendency
to fail, fouling the creation of the python module.  The following
variables should be unchecked

.. code-block:: text

    BUILD_opencv_python_tests
    BUILD_PERF_TESTS
    BUILD_TESTS

Once the configuration is complete, it can be confirmed by observing the 
output of the cmake command.  Verify that the settings are correct before
starting the build, then use the command prompt from the build directory.

.. code-block:: text

    cmake --build . --config Release

After a lengthy compilation, the module can be installed using the command

.. code-block:: text

    cmake --install .

It is now necessary to ammend the path of the computer to include the 
location of the opencv binary dll files, which should be located in a
subdirectory of the build directory, bin/Release.  Add the full path
to this directory to the path environment variable.  For reference, the
environment variables are set in Windows using the applet under 
Settings->About->Advanced System Settings->Environment Variables.  Note
that the command prompt must be re-started to incorporated the new 
setting.

If you are working in a conda environment as recommended, the base 
environment is most likely the location of the opencv module.  You can 
verify by reviewing the PYTHON3_LIBRARY setting used by CMake.  Once
you are in this environment, you can test the installation by invoking the
python shell and successfully importing cv2.

.. code-block:: text

    >  python
    >>> import cv2
    >>> print(cv2.getBuildInformation())
    >>> print(cv2.cuda.getCudaEnabledDeviceCount())

Prior to installing avio, it is necessary to set another environment variable
so the compiler can find OpenCV.  Using the same applet as before, create a 
new environment variable

.. code-block:: text

    OpenCV_DIR = path_to_opencv_build_directory.

There is a further configuration task that must be done before using the 
OpenCV GPU configuration.  This will become apparent if the darknet python
program included with the distribution is used.  There will be an error 
message complaining that the zlibwapi.dll file was not found and should be
placed in the path.  It is possible to find this file online, but will 
require navigating unsavory dll download sites.  The problem can be solved
more easily by finding the zlib.dll file in the python bin folder and copying
it to a new file named zlibwapi.dll in the same folder, as these two file 
share nearly identical functionality.

The placement of the python module can be inconvenient if the desired 
location is elsewhere, e.g. in another conda environment.  This issue
may be resolved by copying the cv2 directoy from the Lib/site-packages
directory into the corresponding location in the desired env folder
in the anaconda directory tree.

