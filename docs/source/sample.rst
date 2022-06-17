Sample Program
==============

.. _test_program:

Test Program
------------

The source code for avio includes a number of sample programs that can be used for learning
about avio works and as a baseline for creating your own custom applications.  The tes.py
program can be used to test the installation of avio and to verify that the host machine has
been configured properly.  It uses a small mp4 file, which is included, as a test source.  
The test program will read the the test.mp4 file and apply simple video and audio filters, 
the write the results to another mp4 file named output.mp4.  This file can be observed with
the ffplay program, which will be included with the ffmpeg program installed by conda.

.. _stats_program:

Stats Program
-------------

The stats program can be used to get information about the media file.  It is invoked with
the name of the file to be observed.  It also has a --show option that will diplay the 
summary content of each packet in the file.  This can be helpful in understanding the 
inner structure of the media file in a troubleshooting situation.

.. _trim_and_merge:

Trim and Merge
--------------

There are two sample programs that can be used for elementary editing of media files.  Trim
will remove unwanted footage from the beginning and/or end of a file.  The program takes
input and output filenames along with the desired starting and ending time of the result in
seconds.  The Merge program will combine any number of files into a single output file.  Note
that the merge requires that the input files have the same format, the most likely scenario
being that all the input files are recorded from the same source.

.. _play:

Play Program
------------

The Play program is a more comprehensive example of an avio application.  It has several options 
that control various functions of the stream process, and can be used with included video callback
programs.  In its simplest form, the program can be invoked using the filename of the media file
to be played.

.. code-block:: text

    python play.py test.mp4

.. rubric::
    no_audio, no_video

It is possible to disable either the video or audio streams using --no_video or --no_audio arguments.
Many of the most common issues associated with an avio application involve something with the audio
stream.  Trying --no_audio will often get the program running, and can be helpful in troubleshooting.

.. code-block:: text

    python play.py test.mp4 --no_audio

.. rubric::
    ffmpeg filters

To invoke ffmpeg filters on the incoming streams, the --vfilter and --afilter directives may be used.
This will be especially important when python video callbacks are used, as the video frames must be 
converted to bgr24 format in order for the python module to properly receive the data as a NumPy 
array.  Another common video filter used often is the scale filter.  A sample video filter directive
with both of the arguments will have the appearance as follows

.. code-block:: text

    python play.py test.mp4 --vfilter scale=640x320,format=bgr24

.. rubric::
    hardware decoding

If the host machine is configured accordingly, the video stream may be decoded in hardware.  This is a 
more efficient use of resources and can improve perfomance, especially if the CPU is underpowered or
under heavy load.  Bear in mind that the proper configuration includes both the hardware and the ffmpeg
libraries to enable hardware decoding.  On windows, the default ffmpeg libraries provided by conda 
forge do include drivers for CUDA while the linux equivalent do not.

.. rubric::
    encoding

The play program can be configured to write the results of the streams to a file.  The configuration
shown in the play program is a fairly simple implementation of the encode function and shows the
basic minimum required for a properly formed output.  There are many parameters that can be adjusted
to affect the various qualities of the output.  Experimentation is recommended when developing an
application that produces output.  Hardware encoding is available with the same caveats as those
discussed in the decoding section above.

The default encoder type is mp4 and can be changed with the --encode_type directive.  Other possible 
values are avi, webm and mkv.

The default filename for output is a system generated name based on the date and time.  The default
directory to which the application will write is the current directory.  These values may be changed
by using the --output_filename and --output_dir directives respectively.

Video encoders can be configured to use a specific h264 profile.  Normally, for for software encoders,
the default is high, and for the CUDA hardware encoder the default is medium.  The setting is accessed
through the Encoder variable profile, and is shown in the play program as a commented line.

The encoder is connected to the build in on screen commands it will toggle operation using the Rec button
visible on the display.  There is also a key code command using the r key that will achieve the same
effect.  Additionally, the application may be configured to start recording upon launch by using the 
writer enabled property.   In the Play application, the --writer_enabled directive will make this setting.

The record button will light red during record and will be white during idle.  If the application has not
configured a writer, the record button will not be visible.  The recording function will cease automatically 
upon termination of the application.

.. rubric::
    on screen controls

avio has a built in GUI for controlling the playback and recording functions.  The GUI resides in the 
picture of the application and is termed the Heads Up Display (HUD).  The GUI will appear automatically 
when the mouse cursor enters the screen area, and will retreat if the mouse becomes inactive or leaves 
the screen.  It some cases, it may be desirable that the GUI is always or never present.  These effects 
may be achieved using the --pin_hud and --disable_hud.

The functions performed by the GUI are available as keyboard shortcuts at all times as shown in the 
On Screen commands.

.. rubric::
    ignore_video_pts

IP cameras have somewhat different characterstics from other types of streams with regard to PTS.  It
is best to process the video streams as they come into the system with out regard to the PTS of a 
particular frame.  The --ignore_video_pts directive will make this setting possible.


.. rubric::
    echo callback

The echo callback program is included as a demonstraticon of the use of a python video callback program.
It shows how the paramaters and data are passed back and forth from the main application to the callback.
The video filter set to format=bgr24 is required for the python callback to work.  The python initialization
string is passed as an argument to the directive.

.. code-block:: text

    python play.py test.mp4 --echo key1=value1;key2=value2 --vfilter format=bgr24

.. rubric::
    darknet callback

The darknet callback program is included as a demonstration of the use of advanced functions using OpenCV.
The callback requires that a valid darknet model be present on the host machine.  Pre trained models can be
found in the Darknet repository https://github.com/AlexeyAB/darknet#pre-trained-models.  The first few
models in the list are for training, look down the page a bit for the ones for inference.

yolov4.cfg - 245 MB: yolov4.weights (Google-drive mirror yolov4.weights ) 
paper Yolo v4 just change width= and height= parameters in yolov4.cfg file 
and use the same yolov4.weights file for all cases:

The arguments to the --darknet directive tell the python callback where to find the model and its cfg file.
There is an additional parameter that the callback accepts that will create a database that will store the 
results of the detections.  This can be useful if you want to try different actions with the results of the 
detections without having to re-run the detector.

Note that the detection will be very slow if the OpenCV configuration does not include GPU functionality.
See the section on compiling OpenCV with GPU for further information.

.. code-block::

    python play.py test.mp4 --darknet cfg=yolov4.cfg;weights=yolov4.weights;db_name=detect.db --vfilter format=bgr24 --no_audio

.. rubric::
    db_read callback

If the db_name option was used during the darknet callback, the database will contain a record of the 
detections found.  The database can be used as a source of the detections and played back with the same
results as running darknet.  This has the advantage of a much faster execution as the complex detection
process has already been baked into the results.

.. code-block::

    python play.py test.mp4 --db_read db_name=detect.db --vfilter format=bgr24

.. rubric::
    deep_sort callback

The sample program comes with an implementation of the deep sort algorithm.  In order to run the callback
some further configuration is necessary.  Add the appropriate version of tensorflow, which is tensorflow-gpu
if the host machine is equipped with GPU hardware, or just tensorflow if it is not.  Also, scipy is needed.
It is best to use pip inside the conda environment to install these modules.

.. code-block:: text

    pip install tensorflow-gpu
    pip install scipy

The deep_sort program requires a tensorflow model for making object comparisons.  A version of the model
compatible with the program is available from https://github.com/sr99622/deep_sort_v2.  Copy the directory
saved_model into the python/deep_sort folder in the avio distribution source code.

The deep_sort program requires initialization arguments for the tensorflow model, the gpu memory limit, and
the input and output databases.  The program reads the detections from the database, assigns a tracking id
to each and writes the result to an output database.  The results can be replayed using the db_read 
callback the same way as shown above.  Unassigned detections are shown in green, and detections which
are assigned to tracks are show in white with the track number.  A good exercise to observe the accuracy
of the track assignments is to pause the stream during db_read and single step back and forth through
the stream using the s and a key shortcuts.

To run the deep sort algorithm on the saved detections use

.. code-block:: text

    python play.py test.mp4 --vfilter format=bgr24 --deep_sort model_name=./deep_sort/saved_model;gpu_mem_limit=6144;db_name_in=detect.db;db_name_out=track.db


To play back the results of the algorithm

.. code-block:: text

    python play.py test.mp4 --db_read db_name=track.db --vfilter format=bgr24
    
.. rubric::
    semantic segmentation

Please refer to https://debuggercafe.com/semantic-segmentation-using-pytorch-fcn-resnet/ for detailed
information on how to implement semantic segmentation using pytorch.

.. code-block:: text

    python play.py test.mp4 --vfilter format=bgr24 --segment
    
.. rubric::
    yolov5

Requires the installation of pytorch and the yolov5 requirements in addition to avio.  See the 
following links to get more detailed information

https://pytorch.org/

https://github.com/ultralytics/yolov5

The command to launch the example includes python initialization for the repository, model name
and the width and height of the video images.

.. code-block:: text

    python play.py test.mp4 --vfilter format=bgr24 --yolov5 repo=ultralytics/yolov5;model=yolov5x6;width=1280;height=720


.. rubric::
    live stream harvesting

By using the yt-dlp program in conjunction with avio, it is possible to harvest media from live streams
from youtube and other media sites.  yt-dlp can be installed with conda forge.  To invoke with avio, use
the stdin pipe as shown below.

.. code-block:: text

    yt-dlp -o - https://www.youtube.com/watch?v=vvOjJoSEFM0 | python play.py pipe: --encode

The record function can then be used to activate recording to store clips from the livestream.

