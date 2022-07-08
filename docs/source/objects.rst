Object Reference
================

.. _reader:

Reader
------

Reader is the object that demultiplexes the raw stream or file data.

.. py:class:: avio.Reader(str desc)

    Initializes the media reader.

    :param desc: Required media description e.g. "sample.mp4".
    :type desc: str

    .. py:method:: duration()

        :return: The duration of the stream in milliseconds.
        :rtype: int

    .. py:method:: start_time()

        Returns the start time of the media, usually zero, but not always.

        :return: The media start time in milliseconds.
        :rtype: int

    .. py:method:: bit_rate()

        Returns the bit rate of the stream.  This determines the density of the compression, which will 
        affect the accuracy of the uncompressed media.  Higher bit rates will render more accurate 
        display at the expense of larger file sizes or higher stream bandwidth.

        :return: The bit rate in bytes
        :rtype: int

    .. py:method:: start_from(int start)

        The reader can be instructed to start from a point in the middle of the stream.

        :param start: The starting point in milliseconds
        :type start: int

    .. py:method:: end_at(int end)

        The reader can be instructed to stop before the end of the stream.

        :param end: The end point in milliseconds
        :type end: int

    .. py:method:: has_video()

        :return: Whether or not the stream has a video component
        :rtype: bool

    .. py:method:: width()

        :return: The width of the video frames in pixels
        :rtype: int

    .. py:method:: height()

        :return: The height of the video frames in pixels
        :rtype: int

    .. py:method:: frame_rate()

        The frame rate of the media is the number of video frames displayed per second.  This parameter 
        will affect the motion accuracy of the video.  Higher frame rates will appear to move more 
        smoothly.  The frame rate is expressed as an AVRational, which is a fraction of two integers.

        :return: The video frame rate
        :rtype: avio.AVRational

    .. py:method:: pix_fmt()

        The pixel format of the video, expressed as a constant.  See the discussion on pixel formats 
        nearby for more detailed information.

        :return: Pixel Format
        :rtype: avio.AVPixelFormat

    .. py:method:: str_pix_fmt()

        :return: The pixel format in a human readable string
        :rtype: str

    .. py:method:: video_codec()

        The codec describes the compression format for the media, expressed as a constant.  See the discussion
        on codecs nearby for more detailed information.

        :return: The codec ID
        :rtype: avio.AVCodecID

    .. py:method:: str_video_codec()

        :return: The codec ID in a human readable string
        :rtype: str

    .. py:method:: video_bit_rate()

        :return: The bit rate of the video component of the multimedia
        :rtype: int

    .. py:method:: video_time_base()

        The time base describes a factor that determines the calculation of the presentation time stamp (pts). 
        See the discussion on pts nearby for more detailed information.

        :return: The video time base
        :rtype: avio.AVRational

    .. py:method:: has_audio()

        :return: Whether or not the stream has an audio component
        :rtype: bool

    .. py:method:: channels()

        :return: Number of audio channels, e.g. stereo = 2
        :rtype: int

    .. py:method:: sample_rate()

        :return: The number of samples per second of audio in the stream
        :rtype: int

    .. py:method:: frame_size()

        :return: The number of samples contained in a single frame of audio data
        :rtype: int

    .. py:method:: channel_layout()

        :return: The audio channel layout of the stream, expressed as a constant
        :rtype: int

    .. py:method:: str_channel_layout()

        :return: The audio channel layout in a human readable string
        :rtype: str

    .. py:method:: sample_format()

        :return: The audio sample format, expressed as a constant
        :rtype: avio.AVSampleFormat

    .. py:method:: str_sample_format()

        :return: The audio sample format in a human readable string
        :rtype: str

    .. py:method:: audio_codec()

        The codec describes the compression format for the media, expressed as a constant.  See the discussion
        on codecs nearby for more detailed information.

        :return: The codec ID
        :rtype: avio.AVCodecID

    .. py:method:: str_audio_codec()

        :return: The codec ID in a human readable string
        :rtype: str

    .. py:method:: audio_bit_rate()

        :return: The bit rate of the audio component of the multimedia
        :rtype: int

    .. py:method:: audio_time_base()

        The time base describes a factor that determines the calculation of the presentation time stamp (pts). 
        See the discussion on pts nearby for more detailed information.

        :return: The audio time base
        :rtype: avio.AVRational

    .. py:method:: video_out()

        :return: The name of the video output queue
        :rtype: str

    .. py:method:: audio_out()

        :return: The name of the audio output queue
        :rtype: str

    .. py:method:: set_video_out(str name)

        :param name: The video output queue name
        :type name: str

    .. py:method:: set_audio_out(str name)

        :param name: The audio output queue name
        :type name: str

    .. py:attribute:: vpq_max_size

        This attribute sets the maximum size of the reader video queue.  For local files, the default 
        value of 1 is a setting that produces good results.  Streams arriving over the network may 
        require a larger buffer to accomodate structural issues or timing delays in order to preserve 
        the data without dropping frames.  The attribute is set by the user.

        :type: int
        :value: 1

    .. py:attribute:: apq_max_size

        This attribute sets the maximum size of the reader audio queue.  For local files, the default 
        value of 1 is a setting that produces good results.  Streams arriving over the network may 
        require a larger buffer to accomodate structural issues or timing delays in order to preserve 
        the data without dropping frames.  The attribute is set by the user if needed.

        :type: int
        :value: 1

    .. py:attribute:: show_video_pkts

        This attribute may be used to observe the characteristics of video packets in the media.  This 
        may be useful when troubleshooting applications.  This attribute is set by the user if desired.

        :type: bool
        :value: False

    .. py:attribute:: show_audio_pkts

        This attribute may be used to observe the characteristics of audio packets in the media.  This 
        may be useful when troubleshooting applications.  This attribute is set by the user if desired.

        :type: bool
        :value: False

.. _decoder:

Decoder
-------

Decoder unpacks the raw data and decompresses it into readable form.

.. py:class:: avio.Decoder(avio.Reader reader, avio.AVMediaType media_type, avio.AVHWDeviceType 
    hw_device_type = AV_HWDEVICE_TYPE_NONE)

    Initializes the decoder.  A Reader is required to feed packets to the decoder.  The user is required to 
    specify the media type for the decoder.  An option for a hardware device is available for use if the 
    host machine is equipped with the appropriate hardware and drivers.

    Note that the Decoder object is a dual purpose entity that provides functionality for both video and 
    audio streams.  The corresponding methods described apply only to the relevant media type being decoded.

    :param reader: Required media reader.
    :type reader: avio.Reader

    :param media_type: Required media type for decoding
    :type media_type: avio.AVMediaType

    :param hw_device_type: Optional hardware device type
    :type hw_device_type: avio.AVHWDeviceType

    .. py:method:: video_in()

        :return:  The name of the video input queue
        :rtype: str
        
    .. py:method:: audio_in()

        :return:  The name of the audio input queue
        :rtype: str
        
    .. py:method:: video_out()

        :return:  The name of the video output queue
        :rtype: str
        
    .. py:method:: audio_out()

        :return:  The name of the audio output queue
        :rtype: str
        
    .. py:method:: set_video_in(str name)

        :param name:  The video input queue name
        :type name: str

    .. py:method:: set_audio_in(str name)

        :param name:  The audio input queue name
        :type name: str
        
    .. py:method:: set_video_out(str name)

        :param name:  The video output queue name
        :type name: str
        
    .. py:method:: set_audio_out(str name)

        :param name:  The audio output queue name
        :type name: str

    .. py:attribute:: show_frames

        This attribute may be used to observe the characteristics of frames produced by 
        the decoder.  This  may be useful when troubleshooting applications.  This 
        attribute is set by the user if desired.

        :type: bool
        :value: False


.. _filter:

Filter
------

Filter performs the initial processing on the decompressed data.

.. py:class:: avio.Filter(avio.Decoder decoder, str desc)

    Initializes the Filter.  A Decoder is required to feed frames to the filter.  

    Note that the Filter object is a dual purpose entity that provides functionality for both video and 
    audio streams.  The corresponding methods described apply only to the relevant media type being filtered.

    :param decoder: Required decoder.
    :type decoder: avio.Decoder

    :param desc: Required string description of the filter operation
    :type desc: str

    .. py:method:: width()
        
        :return:  The width of the frame in pixels
        :rtype: int

    .. py:method:: height()
        
        :return:  The height of the frame in pixels
        :rtype: int

    .. py:method:: pix_fmt()

        :return:  The pixel format of the frame
        :rtype: avio.AVPixelFormat

    .. py:method:: sample_rate()

        :return:  The sample rate of the stream
        :rtype: int

    .. py:method:: channels()

        :return:  The number of channels of the stream
        :rtype: int

    .. py:method:: channel_layout()

        :return:  The channel layout of the stream
        :rtype: int

    .. py:method:: sample_format()

        :return:  The sample format of the stream
        :rtype: avio.AVSampleFormat

    .. py:method:: frame_size()

        :return:  The frame size the stream
        :rtype: int

    .. py:method:: video_in()

        :return:  The name of the video input queue
        :rtype: str
        
    .. py:method:: audio_in

        :return:  The name of the audio input queue
        :rtype: str
        
    .. py:method:: video_out

        :return:  The name of the video output queue
        :rtype: str
        
    .. py:method:: audio_out

        :return:  The name of the audio output queue
        :rtype: str
        
    .. py:method:: set_video_in(str name)

        :param name:  The video input queue name
        :type name: str

    .. py:method:: set_audio_in(str name)

        :param name:  The audio input queue name
        :type name: str
        
    .. py:method:: set_video_out(str name)

        :param name:  The video output queue name
        :type name: str
        
    .. py:method:: set_audio_out(str name)

        :param name:  The audio output queue name
        :type name: str


.. _display:

Display
-------

Display handles the presentation of the media.  It also hosts the python interface.

.. py:class:: avio.Display(avio.Reader reader)

    Initializes the display.

    :param reader: Required application reader
    :type desc: avio.Reader

    .. py:attribute:: audio_playback_format

        This attribute can be used to change the playback format for audio.  The default is S16

        :type: avio.AVSampleFormat

    .. py:attribute:: disable_audio

        This attribute can be used to ignore audio streams.  Useful if the audio subsystem is not 
        working for some reason

        :type: bool

    .. py:attribute:: hud_enabled

        If set to False, the application will not show the HUD

        :type: bool

    .. py:attribute:: ignore_video_pts

        This attribute will cause the application to ignore time stamps on video frames.  Useful for 
        IP cameras

        :type: bool

    .. py:attribute:: recent_q_size

        The application will maintain a queue of recent video frames, for single step review in reverse 
        time order. Default size is 200

        :type: int

    .. py:attribute:: prepend_recent_write

        If this attribute is set to True, the application will include the recent queue when writing.  
        Note that audio should be disabled if using this option as the queue does not retain audio frames 
        and the output will be distorted if audio is not disabled.

        :type: bool

    .. py:attribute:: font_file

        The application will attempt to find this attribute automatically, which will enable the HUD.  
        In the event that does not work, the user may assign the attribute manually.

        :type: str

    .. py:method:: pin_hud(bool pinned)

        Setting with True will force the HUD to display at all times

        :type name: bool

    .. py:method:: video_in()

        :return:  The name of the video input queue
        :rtype: str
        
    .. py:method:: audio_in

        :return:  The name of the audio input queue
        :rtype: str
        
    .. py:method:: video_out

        :return:  The name of the video output queue
        :rtype: str
        
    .. py:method:: audio_out

        :return:  The name of the audio output queue
        :rtype: str
        
    .. py:method:: set_video_in(str name)

        :param name:  The video input queue name
        :type name: str

    .. py:method:: set_audio_in(str name)

        :param name:  The audio input queue name
        :type name: str
        
    .. py:method:: set_video_out(str name)

        :param name:  The video output queue name
        :type name: str
        
    .. py:method:: set_audio_out(str name)

        :param name:  The audio output queue name
        :type name: str


.. _writer:

Writer
------

Writer will compress the data and write it to stream or file.

.. py:class:: avio.Writer(str desc)

    Initializes the writer.  A description string for the type of file to be written is required.  The
    string that specifies the file type corresponds to the file extension of the type.  Typical cases 
    include "mp4", "webm", "mkv", "mov", "avi".

    :param desc: Required description.
    :type desc: str

    .. py:attribute:: write_dir

        This attribute can be used to instruct the writer to write to a directory other than the system
        default video directory.  This attribute is set by the user if desired.

        :type: str
        :value: A str representing the default video directory

    .. py:attribute:: filename

        This attribute can be used to set the filename of the writer output.  If not set, the system 
        will automatically use a datetime string representing the time when the writing process began.

        :type: str
        :value": A str representing the current datetime

    .. py:attribute:: show_video_pkts

        This attribute may be used to observe the characteristics of video packets in the media.  This 
        may be useful when troubleshooting applications.  This attribute is set by the user if desired.

        :type: bool
        :value: False

    .. py:attribute:: show_audio_pkts

        This attribute may be used to observe the characteristics of audio packets in the media.  This 
        may be useful when troubleshooting applications.  This attribute is set by the user if desired.

        :type: bool
        :value: False

.. _encoder:

Encoder
-------

Encoder is the codec manager for compressing data.

.. py:class:: avio.Encoder(avio.Writer writer, avio.AVMediaType media_type)

    Initializes the Encoder.  A Writer is required to manage the encoder and media.  

    Note that the Encoder object is a dual purpose entity that provides functionality for both video and 
    audio streams.  The corresponding methods described apply only to the relevant media type being filtered.

    :param writer: Required writer.
    :type writer: avio.Writer

    :param media_type: The media type handled by the Encoder
    :type media_type: avio.AVMediaType

    .. py:attribute::  pix_fmt

        :type: avio.AVPixelFormat

    .. py:attribute::  width

        :type: int

    .. py:attribute::  height

        :type: int

    .. py:attribute::  video_bit_rate

        :type: int

    .. py:attribute::  frame_rate

        :type: int

    .. py:attribute::  gop_size

        :type: int

    .. py:attribute::  video_time_base

        :type: avio.AVRational

    .. py:attribute::  profile

        :type: str

    .. py:attribute::  hw_video_codec_name

        :type: str

    .. py:attribute::  hw_device_type

        :type: avio.AVHWDeviceType

    .. py:attribute::  hw_pix_fmt

        :type: avio.AVPixelFormat

    .. py:attribute::  sw_pix_fmt

        :type: avio.AVPixelFormat

    .. py:attribute::  sample_fmt

        :type: avio.AVSampleFormat

    .. py:attribute::  channel_layout

        :type: int

    .. py:attribute::  audio_bit_rate

        :type: int

    .. py:attribute::  sample_rate

        :type: int

    .. py:attribute::  nb_samples

        :type: int

    .. py:attribute::  channels

        :type: int

    .. py:attribute::  audio_time_base

        :type: avio.AVRational

    .. py:method:: set_channel_layout_mono()

        :rtype: void

    .. py:method:: set_channel_layout_stereo()

        :rtype: void

    .. py:attribute:: frame_q_max_size

        This attribute can be used to set the maximum size of the input queue to the encoder. This is 
        used when the preprend_recent_write flag is set and the encoder causes the video to stutter.  
        A good value to try is to match the value of the recent_q_size.

        :type:: int

    .. py:method:: video_in()

        :return:  The name of the video input queue
        :rtype: str
        
    .. py:method:: audio_in

        :return:  The name of the audio input queue
        :rtype: str
        
    .. py:method:: video_out

        :return:  The name of the video output queue
        :rtype: str
        
    .. py:method:: audio_out

        :return:  The name of the audio output queue
        :rtype: str
        
    .. py:method:: set_video_in(str name)

        :param name:  The video input queue name
        :type name: str

    .. py:method:: set_audio_in(str name)

        :param name:  The audio input queue name
        :type name: str
        
    .. py:method:: set_video_out(str name)

        :param name:  The video output queue name
        :type name: str
        
    .. py:method:: set_audio_out(str name)

        :param name:  The audio output queue name
        :type name: str

.. _process:

Process
-------

.. py:class:: avio.Process()

    Process is the main object of an avio application.  It bundles the selected component objects into 
    a threaded framework and launches with the run command.  The order in which objects are added is not 
    critical, but it may be helpful to view the system in terms of data flow through the components. 
    Additionally, the process object may be used to trim and merge media files.

    .. py:method:: add_reader(avio.Reader reader)  

        :param reader: The application reader, one per application
        :type reader: avio.Reader

    .. py:method:: add_decoder(avio.Decoder decoder)

        :param decoder: Decodes the reader output, one for each media type
        :type decoder: avio.Decoder

    .. py:method:: add_filter(avio.Filter filter)

        :param filter: Filters the decoded frames, one for each decoder (optional)
        :type filter: avio.Filter

    .. py:method:: add_display(avio.Display display)

        :param display: Displays the video and audio frames, one per application
        :type display: avio.Display

    .. py:method:: set_python(avio.Display, str file_path, str python_class)

        :param display: The application display
        :type display: avio.Display

        :param file_path: The name of the python file used to process video frames
        :type file_path: str

        :param python_class: The name of the python Class
        :type python_class: str

    .. py:method:: set_python_init_arg(Display, str arg)

        :param arg: The string used to initialized the python Class
        :type arg: str
        
    .. py:method:: add_encoder(avio.Encoder encoder)

        :param encoder: The encoder for the media, one for each type
        :type encoder: avio.Encoder

    .. py:method:: add_frame_drain(str frame_q_name)

        :param frame_q_name: The name of the queue to be drained
        :type frame_q_name: str

    .. py:method:: add_packet_drain(str pkt_q_name)

        :param pkt_q_name: The name of the queue to be drained
        :type pkt_q_name: str

    .. py:method:: run()

        This method takes no arguments

    .. py:method:: trim(str in_filename, str out_filename, int start, int end)

        :param in_filename: The name of the media file to be trimmed
        :type in_filename: str

        :param out_filename: The name of the output file
        :type out_filename: str

        :param start: The starting point of the trim, in milliseconds
        :type start: int

        :param end: The end point of the trim, in milliseconds
        :type end: int

    .. py:method:: merge(str out_filename)

        Note that input file names are assigned to the merge_filenames varaible prior to invocation of this command

        :param out_filename: The name of the output file.  
        :type out_filename: str

    .. py:attribute:: merge_filenames(tuple[str] filenames)

        :param filenames: The media files to be merged
        :type filenames: tuple[str]

.. _avrational:

AVRational
----------

AVRational is used to define ratios.

.. py:class:: avio.AVRational()

    This class is used by ffmpeg to define ratios referenced in media streams, mostly related to time factors.
    There are several function calls that return this type, and Encoders may require this as an input 
    parameter.  It has only two fields, num and den, which are the numerator and denominator of the fraction 
    repsectively.  When assigning a value of this type, the variable is instantiated with no arguments.  This 
    results in zero values for num and den, which can subsequently be assigned to their desired values.  If 
    the decimal equivalent of the number is required, convert num and den to floats and then divide.

    .. py:attribute:: num

        The numerator of the ratio fraction

        :type: int
        :value: 0

    .. py:attribute:: den

        The denominator of the ratio fraction

        :type: int
        :value: 0

.. _constants:

Constants
---------

Various constants used to define media characteristics.

.. c:enum:: avio.AVMediaType

    AVMEDIA_TYPE_VIDEO

    AVMEDIA_TYPE_AUDIO

    AVMEDIA_TYPE_UNKNOWN

.. c:enum:: avio.AVPixelFormat

    AV_PIX_FMT_YUV420P

    AV_PIX_FMT_BGR24

    AV_PIX_FMT_RGB24

    AV_PIX_FMT_NV12

    AV_PIX_FMT_NV21

    AV_PIX_FMT_RGBA

    AV_PIX_FMT_BGRA

    AV_PIX_FMT_VAAPI

    AV_PIX_FMT_CUDA

    AV_PIX_FMT_QSV

    AV_PIX_FMT_D3D11VA_VLD

    AV_PIX_FMT_VDPAU

    AV_PIX_FMT_D3D11

    AV_PIX_FMT_OPENCL
        
    AV_PIX_FMT_GRAY8

    AV_PIX_FMT_NONE

.. c:enum:: avio.AVHWDeviceType
        
    AV_HWDEVICE_TYPE_CUDA

    AV_HWDEVICE_TYPE_VDPAU

    AV_HWDEVICE_TYPE_VAAPI

    AV_HWDEVICE_TYPE_DXVA2

    AV_HWDEVICE_TYPE_QSV

    AV_HWDEVICE_TYPE_VIDEOTOOLBOX

    AV_HWDEVICE_TYPE_D3D11VA

    AV_HWDEVICE_TYPE_DRM

    AV_HWDEVICE_TYPE_OPENCL

    AV_HWDEVICE_TYPE_MEDIACODEC

    AV_HWDEVICE_TYPE_NONE

.. c:enum:: avio.AVSampleFormat

    AV_SAMPLE_FMT_U8

    AV_SAMPLE_FMT_S16

    AV_SAMPLE_FMT_S32

    AV_SAMPLE_FMT_FLT

    AV_SAMPLE_FMT_DBL

    AV_SAMPLE_FMT_U8P

    AV_SAMPLE_FMT_S16P

    AV_SAMPLE_FMT_S32P

    AV_SAMPLE_FMT_FLTP

    AV_SAMPLE_FMT_DBLP

    AV_SAMPLE_FMT_S64

    AV_SAMPLE_FMT_S64P

    AV_SAMPLE_FMT_NB

    AV_SAMPLE_FMT_NONE


