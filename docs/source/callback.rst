Python Video Callback
=====================

.. _python_video_callback:

Introduction
------------

avio has a built in mechanism for processing video frames during stream
playback.  If configured to do so, avio will send each video frame to a 
developer defined python class for additional processing.  This gives the 
developer the ability to manipulate all of the pixels in the frame 
individually, or the characteristics of the entire frame such as resolution, 
or cropping.  Any python module that can operate on images can be used in 
the callback, enabling the use of advanced algorithms such as those found in 
tensorflow or pytorch.

.. _format_conversion:

Format Conversion (IMPORTANT)
-----------------------------

It is required to convert the format of the video frame before sending its
data to the callback.  Video frames are generally presented in YUV420 format
which is not compatible with a NumPy array format.  For OpenCV, the format
used to represent video frames is BGR24.  In order to convert the frame to a
compatible format, the avio application should include a video filter and the
argument to the filter should include "format=bgr24".

If your application produces the message "Error: unsupported pix fmt.  If you 
intend to convert the frame to cv::Mat format, the incoming frame must be in 
either bgr24 or bgra pixel format", you have not included this step.

.. _callback_registration:

Callback Registration
---------------------

In order for the callback to be instantiated and executed by the parent avio
application, it must first be registered with the application.  The callback
is hosted in the display module, and is registered by the process.  The 
registration needs to know the filename of the python class and the class name
itself.  If the class requires an initialization string, that is added to the
display as well.

The code below shows the registration for the echo sample program.

.. code-block:: python

    process.set_python(display, "./echo.py", "Echo")
    process.set_python_init_arg(display, "test=test_config")


.. _initialization_string:

Initialization
--------------

Variables required for initialization in the callback object may be sent from 
avio in an initialization string.  The string takes the form of
key1=value1;key2=value2 ...  It is the repsonsibility of the callback developer
to parse the string in the constructor of the callback object.  The initialization
string is not required if the callback object does not need one.

.. _video_frame_data:

Video Frame Data
----------------

The frame data is converted by avio into a NumPy array that is compatible with 
the opencv mat format.  Note that the data tranfer between avio and the python 
callback is done by reference, meaning that the data itself resides in the 
same memory location, and only a pointer to the data is transferred between the 
two programs.  This makes the process very efficient and can accomodate real 
time operation.

.. _presentation_time_stamp:

Presentation Time Stamp (PTS)
-----------------------------

In addition to the image data, the main process will send the presentation time 
stamp (PTS) of the frame, and a normalized real time stamp (RTS).  The difference 
between these two time stamps is that the PTS is a factored representation of the 
time stamp based on the time base of the video stream.  There are some issues with 
processing this variable.  The PTS is defined as a 64 bit integer, which is too 
large to pass through the data boundary between the main application and the python 
callback.  The PTS is therefore converted to a string equivalent before it is sent 
to the python callback.  The callback must then convert the PTS back to an int for 
use in that form.  Note again that the PTS is a factored version of the time stamp 
based on the time base of the video stream.

.. _real_time_stamp:

Real Time Stamp
---------------

avio will also send another variable called RTS (Real Time Stamp). The RTS is a more 
simplistic representation of the timestamp.  It is simply an integer representing the 
number of milliseconds elapsed since the start of the video, and may often be an easier 
value to work with for identifying individual frames if the PTS is not explicitly needed.

.. _events:

Events
------

The main process will also send a string representing the contents of the event 
queue to the python callback.  The developer may parse the string to process mouse 
and keyboard events produced by the user.

During initialization, the main process may send paramters to the python callback 
class. A string of key value pairs may be sent using the syntax key1=value1;key2=value2. 
The developer is responsible for parsing the string in the python callback.

.. _return_values:

Return Values
-------------

At the completion of the python code, the developer may optionally return the values 
to the main process.  This is useful if the image has been changed, as the display 
will show the changed image in that case for viewing by the user.  The PTS value may 
also be changed and returned to the main process.  This is useful in situations where 
the PTS values of the original frames need to be adjusted when recording.

.. _recording_trigger:

Recording Trigger
-----------------

There is another parameter that the python callback can send to the main process that 
will trigger the Writer to start recording.  This can be useful in a real time 
application that will start recording when a condition is met, for example the presence 
of a person in the picture.  The variable should be returned to the main application as 
False for each frame, then a True value will toggle the recording mechanism from on to 
off or vice versa.

The developer may return any of these variables, none or a combination of two.  If more
than one of the variable is returned, the order matters, and should be image, PTS, record.

.. _echo_program:

Echo Program
------------

The sample echo program demonstrates the use of the callback.  The avio application that 
sends data to this callback must register the callback as shown above.

.. code-block:: python

    class Echo:
        def __init__(self, arg):
            print("echo.__init__")

            self.mask = ""
            self.button = ""
            self.clicks = 0
            self.x = 0
            self.y = 0

            self.keysym = ""
            self.keymod = ""
            self.repeat = 0

            # parse the initialzation string
            unpacked_args = arg[0].split(";")
            for line in unpacked_args:
                key_value = line.split("=")
                print("key  ", key_value[0])
                print("value", key_value[1])

        def __call__(self, arg):

            img = arg[0][0]
            print("image shape", img.shape)
            pts = arg[1][0]
            print("pts", pts)
            rts = arg[2][0]
            print("rts", rts)
            events = arg[3][0].split(';')
            for event in events:
                e = event.split(',')
                if e[0] == "SDL_MOUSEMOTION":
                    self.mask = e[1]
                    self.x = int(e[2])
                    self.y = int(e[3])
                    print(self.x, self.y, self.mask)
                if e[0] == "SDL_MOUSEBUTTONDOWN" or e[0] == "SDL_MOUSEBUTTONUP":
                    self.button = e[1]
                    self.clicks = int(e[2])
                    self.x = int(e[3])
                    self.y = int(e[4])
                    print(self.x, self.y, self.clicks, self.button)
                if e[0] == "SDL_KEYDOWN" or e[0] == "SDL_KEYUP":
                    self.repeat = int(e[1])
                    self.keysym = e[2]
                    self.keymod = e[3]
                    print(self.keysym, self.keymod, self.repeat)
            

            # Possible return arguments

            #return img
            #return pts
            #return False

            #return (img, pts, False)
            #return (img, pts)
            #return (img, False)