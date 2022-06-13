How To
======

.. _reader_usage:


Reader Usage
------------

The reader is always the first module in the application and it will take data from 
the network or file system and de-multiplex it into packets for consumption by
downstream modules.  The reader takes one argument in its constructor, which is the
filename or url of the source data.  Additionally, there is a special url "pipe:" 
for reading data from the standard input.

Examples:

Read from file

.. code-block:: python

    reader = avio.Reader("test.mp4")

Read from camera

.. code-block:: python

    reader = avio.Reader("rtsp://admin:admin123@192.168.1.11:88/videoMain")

Read from stdin

.. code-block:: python

    reader = avio.Reader("pipe:")


Once the reader has be instantiated, it is possible to retrieve a wide variety of 
parameters describing the media, examples shown below are taken from the stats.py
sample program included with the distribution.

.. code-block:: python

        seconds = int((reader.duration()/1000)%60)
        minutes = int((reader.duration()/(1000*60))%60)
        print("\nMedia start time:", "{:.3f}".format(float(reader.start_time()/ 1000)))
        print("Media Duration:  ", str(minutes) + ":" + "{:02d}".format(seconds))
        if (reader.has_video()):
            print("\nVideo")
            print("  width:          ", reader.width())
            print("  height:         ", reader.height())
            print("  pixel format:   ", reader.str_pix_fmt())
            print("  video codec:    ", reader.str_video_codec())
            print("  video bit rate: ", reader.video_bit_rate())
            print("  frame rate:     ", reader.frame_rate().num, "/", reader.frame_rate().den)
            fps =  "{:.2f}".format(reader.frame_rate().num/reader.frame_rate().den)
            print("  fps =", fps)
            print("  video time base:", reader.video_time_base().num, "/", reader.video_time_base().den)
        if (reader.has_audio()):
            print("\nAudio")
            print("  channels:       ", reader.channels())
            print("  channel layout: ", reader.str_channel_layout())
            print("  sample rate:    ", reader.sample_rate())
            print("  frame size:     ", reader.frame_size())
            print("  sample format:  ", reader.str_sample_format())
            print("  audio codec:    ", reader.str_audio_codec())
            print("  audio bit rate: ", reader.audio_bit_rate())
            print("  audio time base:", reader.audio_time_base().num, "/", reader.audio_time_base().den)
        print()

If the reader is going to be used by downstream modules, it is necessary to assign names
to the output queues of the reader.  As a note, the avio convention for queue ownership is
that the module that writes data to the queue is considered to be the queue owner.  Queue
names are arbitrary, but a good convention to follow is apq_reader for audio packet out and
vpq_reader for video packet out for the reader.  To assign these names to the reader, the 
following code could be used.

.. code-block:: python

    if reader.has_video():
        reader.set_video_out("vpq_reader")
 
    if reader.has_audio():
        reader.set_audio_out("apq_reader")
 

.. _process_usage:

Process Usage
-------------

With the instantiation of a reader, it is now possible to create a minimal application 
using the Process object.  The process is created, the reader is a created and added to 
the process.  In the code shown below, two packet drains are added to the process.  This
is necessary for the application to start and run, as the reader will be blocked from 
writing any data on the queue unless the queue is emptied.  This is an important feature
regarding how the application works.  The queues control the flow of data between modules
so that downstream modules have time to finish their tasks before upstream modules can
put more data on the queue.

The following code shows how to construct this minimal application, which will open the 
file for the reader, then display a summary of each packet in the file.  The file used
here "test.mp4" is included in the distribution.  The code is taken from the stats.py
file which is also included in the distribution.

.. code-block:: python

    import avio

    process = avio.Process()
    reader = avio.Reader("test.mp4")

    if reader.has_video():
        reader.set_video_out("vpq_reader")
        reader.show_video_pkts = True
        process.add_packet_drain(reader.video_out())

    if reader.has_audio():
        reader.set_audio_out("apq_reader")
        reader.show_audio_pkts = True
        process.add_packet_drain(reader.audio_out())

    process.add_reader(reader)
    process.run()
    

The output of the application goes to the console, which is a summary listing of the 
packets in the media file.  Here is possible to observe the features of the packets in
some detail, which may provide insight into the nature of the media.

.. code-block:: text

    index: 0 flags: 1 pts: 0 dts: -3 size: 104503 duration: 512
    index: 1 flags: 1 pts: 0 dts: 0 size: 23 duration: 1024
    index: 1 flags: 1 pts: 1024 dts: 1024 size: 463 duration: 1024
    index: 0 flags: 0 pts: 1974 dts: 486 size: 3107 duration: 512
    index: 0 flags: 0 pts: 489 dts: 487 size: 227 duration: 512
    index: 1 flags: 1 pts: 2048 dts: 2048 size: 361 duration: 1024
    index: 1 flags: 1 pts: 3072 dts: 3072 size: 344 duration: 1024
    index: 0 flags: 0 pts: 979 dts: 977 size: 131 duration: 512
    index: 1 flags: 1 pts: 4096 dts: 4096 size: 342 duration: 1024
    index: 0 flags: 0 pts: 1484 dts: 1482 size: 357 duration: 512
    index: 1 flags: 1 pts: 5120 dts: 5120 size: 345 duration: 1024
    index: 1 flags: 1 pts: 6144 dts: 6144 size: 344 duration: 1024
    index: 1 flags: 1 pts: 7168 dts: 7168 size: 337 duration: 1024
    index: 0 flags: 0 pts: 3949 dts: 2461 size: 4634 duration: 512
    index: 0 flags: 0 pts: 2464 dts: 2462 size: 396 duration: 512
    index: 1 flags: 1 pts: 8192 dts: 8192 size: 337 duration: 1024
    index: 1 flags: 1 pts: 9216 dts: 9216 size: 345 duration: 1024
    index: 0 flags: 0 pts: 2969 dts: 2967 size: 555 duration: 512
    index: 1 flags: 1 pts: 10240 dts: 10240 size: 343 duration: 1024
    index: 0 flags: 0 pts: 3459 dts: 3457 size: 647 duration: 512
    index: 1 flags: 1 pts: 11264 dts: 11264 size: 349 duration: 1024
    index: 1 flags: 1 pts: 12288 dts: 12288 size: 351 duration: 1024
    index: 1 flags: 1 pts: 13312 dts: 13312 size: 350 duration: 1024

    ...

.. _decoder_usage:

Decoder Usage
-------------

The packets produced by the reader must be decoded if they are to be used in a display 
or some other purpose.  The decoders connect to the reader through the reader output 
queues.  There is one decoder for video, and another for audio.  It is not required to 
decode both streams if that is the desired behavior, the application can be instructed 
to discard either stream.  

The decoder takes the arguments of the reader and the media type.  There is an optional 
argument in the constructor for a hardware device type.  Whether this argument will 
have an effect will depend upon the underlying ffmpeg library.  There are conditional 
switches that must be used during the compilation of ffmpeg that determine the 
configuration with regards to hardware decoding.  Windows versions of pre-compiled 
ffmpeg libraries installed from conda-forge will have these features included 
automatically.  If the host computer is Linux, it is necessary to compile ffmpeg from 
source.  Obviously, the required hardware and drivers will need to be installed on the 
host machine.  CUDA is the most common hardware decoder and will run  properly on most 
recent vintage NVIDIA cards.  Note that hardware decoding is available for video 
streams only.

As in the case of the reader, it is necessary to assign a name to the output queue of the
decoder.  Additionally, the input queue to the decoder is connected to the output queue
of the reader.  In the sample application below, the output of the decoders is connected 
to a frame drain.  The same principle shown above applies, in that it is necessary to 
drain the outputs of the decoder so that it may continue to write data onto the queue.

.. code-block:: python

    import avio

    process = avio.Process()
    reader = avio.Reader("test.mp4")
    process.add_reader(reader)

    if (reader.has_video()):
        reader.set_video_out("vpq_reader")
        videoDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_VIDEO)
        videoDecoder.set_video_in(reader.video_out())
        videoDecoder.set_video_out("vfq_decoder")
        videoDecoder.show_frames = True
        process.add_decoder(videoDecoder)
        process.add_frame_drain(videoDecoder.video_out())

    if (reader.has_audio()):
        reader.set_audio_out("apq_reader")
        audioDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_AUDIO)
        audioDecoder.set_audio_in(reader.audio_out())
        audioDecoder.set_audio_out("afq_decoder")
        audioDecoder.show_frames = True
        process.add_decoder(audioDecoder)
        process.add_decoder(audioDecoder)
        process.add_frame_drain(audioDecoder.audio_out())

    process.run()

The output of the application goes to the console, which is a summary listing of the 
frames produced by the decoders.  Here is possible to observe the features of the packets 
in some detail.

.. code-block:: text

    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 0, m_rts: 0
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 1024, m_rts: 21
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 2048, m_rts: 42
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 3072, m_rts: 64
    VIDEO FRAME, width: 1280 height: 720 format: yuv420p pts: 0 m_rts: 0
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 4096, m_rts: 85
    VIDEO FRAME, width: 1280 height: 720 format: yuv420p pts: 489 m_rts: 32
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 5120, m_rts: 106
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 6144, m_rts: 128
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 7168, m_rts: 149
    VIDEO FRAME, width: 1280 height: 720 format: yuv420p pts: 979 m_rts: 65
    VIDEO FRAME, width: 1280 height: 720 format: yuv420p pts: 1484 m_rts: 99
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 8192, m_rts: 170
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 9216, m_rts: 192
    VIDEO FRAME, width: 1280 height: 720 format: yuv420p pts: 1974 m_rts: 132
    AUDIO FRAME, nb_samples: 1024, channels: 2, format: fltp, sample_rate: 48000, channel_layout: stereo, pts: 10240, m_rts: 213
    VIDEO FRAME, width: 1280 height: 720 format: yuv420p pts: 2464 m_rts: 165    

    ...

.. _display_usage:

Display Usage
-------------

Once the packets have been decoded into frames, it is now possible to present the output to 
the user.  The Display module will present both video and audio frames.  It is worthwhile to 
note that the paths for these two types of stream are quite different.  A characteristic of
the video display is that it must run in the main thread of the application.  Conversely, 
the audio stream must run in its own thread which is independent of the other threads in the
application.  

When the display presents this to the user, the video and audio must be synchronized in order 
to preserve the integrity of the representation by the media.  There are tags associated with 
each frame in both types of streams called the presentation time stamp (PTS).  The PTS is a 
representation of the time at which a particular frame should be presented to the user and is 
factored by a stream parameter called the time base.  The time base in audio and video 
streams will be different, so the application must convert the PTS to a value that corresponds 
to the real time that a frame should present.  This conversion is handled behind the scenes by 
avio and is represented in a frame variable named m_rts.

The display will also need to know the characteristics of the individual streams so that it
may present the frames properly.  In the case of video streams, the display is able to get
the data it needs from the stream itself.  However, in the case of audio streams, the display
must be told ahead of time what parameters to expect.  For this reason, the developer is
required to set parameters for audio streams, but not video.  Future versions of avio will
hopefully be able to auto configure for audio, but for now, this is the case.

The parameters required for audio configuration are listed below.  These parameters may be
obtained from either the audio decoder itself, or the corresponding audio filter.  Note 
that in the underlying ffmpeg code that frame_size and nb_samples are used interchangeably.

.. code-block:: python

    Display.sample_rate
    Display.channels
    Display.channel_layout
    Display.sample_format
    Display.frame_size

The code below shows a simple application with the display configured.  As with other modules,
the display gets data from queues attached to the previous module in the chain.

.. code-block:: python

    import avio

    process = avio.Process()
        
    reader = avio.Reader("test.mp4")
    reader.set_video_out("vpq_reader")
    reader.set_audio_out("apq_reader")

    videoDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_VIDEO)
    videoDecoder.set_video_in(reader.video_out())
    videoDecoder.set_video_out("vfq_decoder")

    audioDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_AUDIO)
    audioDecoder.set_audio_in(reader.audio_out())
    audioDecoder.set_audio_out("afq_decoder")

    display = avio.Display(reader)
    display.set_video_in(videoDecoder.video_out())

    display.set_audio_in(audioDecoder.audio_out())
    display.sample_rate = audioDecoder.sample_rate()
    display.channels = audioDecoder.channels()
    display.channel_layout = audioDecoder.channel_layout()
    display.sample_format = audioDecoder.sample_format()
    display.frame_size = audioDecoder.frame_size()
    display.audio_playback_format = avio.AV_SAMPLE_FMT_U8

    process.add_reader(reader)
    process.add_decoder(videoDecoder)
    process.add_decoder(audioDecoder)
    process.add_display(display)

    process.run()

.. _filter_usage:

Filter Usage
-------------

Filters are used to modify media data.  They are the same filters used in ffmpeg and will 
respond the the same commands.  A reference can be found at this link `ffmpeg filters 
<https://ffmpeg.org/ffmpeg-filters.html>`_ .  

Filters take their input from decoders and send output to the display.  The filter 
constructor arguments are the decoder and the string command for the filter.  Note that
the filter can be set to pass through operation by using the string "null" for video
filters and "anull" for audio filters.

By modifying the code above to include filters, it is possible to demonstrate their use.
Note that the display audio parameters should now reflect the state of the audio filter.

.. code-block:: python

    import avio

    process = avio.Process()
        
    reader = avio.Reader("test.mp4")
    reader.set_video_out("vpq_reader")
    reader.set_audio_out("apq_reader")

    videoDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_VIDEO)
    videoDecoder.set_video_in(reader.video_out())
    videoDecoder.set_video_out("vfq_decoder")

    videoFilter = avio.Filter(videoDecoder, "vflip")
    videoFilter.set_video_in(videoDecoder.video_out())
    videoFilter.set_video_out("vfq_filter")

    audioDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_AUDIO)
    audioDecoder.set_audio_in(reader.audio_out())
    audioDecoder.set_audio_out("afq_decoder")

    audioFilter = avio.Filter(audioDecoder, "aphaser=type=t:speed=2:decay=0.6")
    audioFilter.set_audio_in(audioDecoder.audio_out())
    audioFilter.set_audio_out("afq_filter")

    display = avio.Display(reader)
    display.set_video_in(videoFilter.video_out())

    display.set_audio_in(audioFilter.audio_out())
    display.sample_rate = audioFilter.sample_rate()
    display.channels = audioFilter.channels()
    display.channel_layout = audioFilter.channel_layout()
    display.sample_format = audioFilter.sample_format()
    display.frame_size = audioFilter.frame_size()
    display.audio_playback_format = avio.AV_SAMPLE_FMT_FLT

    process.add_reader(reader)
    process.add_decoder(videoDecoder)
    process.add_filter(videoFilter)
    process.add_decoder(audioDecoder)
    process.add_filter(audioFilter)
    process.add_display(display)

    process.run()

.. _encoder_usage:

Encoder Usage
-------------

Encoders compress media data and write it to file or network.  An encoder will take the 
raw data produced by previous steps in the application and compress it according to the
configuration specified by the developer.  As such, it is necessary to construct the 
encoder configuration carefully to avoid errors.  A knowledge of how media files are 
structured will help in this process.

The encoder constructor takes a writer and a media type identifer, so it is necessary 
to first construct a Writer object before an encoder.  To note here, the writer is not
explicity added to the process object, it is implied through the encoder.

THe code above can be modified to include a pair of encoders that will produce a media
file.  The video encoder includes some commands for hardware encoding that have been 
commented out, if the host system is hardware enabled, these commands can be uncommented
to make use of the GPU encoding.

.. code-block:: python

    import avio

    process = avio.Process()
        
    reader = avio.Reader("test.mp4")
    reader.set_video_out("vpq_reader")
    reader.set_audio_out("apq_reader")

    videoDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_VIDEO)
    videoDecoder.set_video_in(reader.video_out())
    videoDecoder.set_video_out("vfq_decoder")

    videoFilter = avio.Filter(videoDecoder, "hflip")
    videoFilter.set_video_in(videoDecoder.video_out())
    videoFilter.set_video_out("vfq_filter")

    audioDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_AUDIO)
    audioDecoder.set_audio_in(reader.audio_out())
    audioDecoder.set_audio_out("afq_decoder")

    audioFilter = avio.Filter(audioDecoder, "aphaser=type=t:speed=2:decay=0.6")
    audioFilter.set_audio_in(audioDecoder.audio_out())
    audioFilter.set_audio_out("afq_filter")

    display = avio.Display(reader)
    display.set_video_in(videoFilter.video_out())

    display.set_audio_in(audioFilter.audio_out())
    display.sample_rate = audioFilter.sample_rate()
    display.channels = audioFilter.channels()
    display.channel_layout = audioFilter.channel_layout()
    display.sample_format = audioFilter.sample_format()
    display.frame_size = audioFilter.frame_size()
    display.audio_playback_format = avio.AV_SAMPLE_FMT_FLT

    display.set_video_out("vfq_display")
    display.set_audio_out("afq_display")

    writer = avio.Writer("mp4")
    writer.filename = "output.mp4"
    writer.enabled = True

    videoEncoder = avio.Encoder(writer, avio.AVMEDIA_TYPE_VIDEO)
    videoEncoder.set_video_in(display.video_out())
    videoEncoder.set_video_out("vpq_encoder")

    videoEncoder.pix_fmt = avio.AV_PIX_FMT_YUV420P
    videoEncoder.width = videoFilter.width()
    videoEncoder.height = videoFilter.height()
    videoEncoder.frame_rate = int(reader.frame_rate().num / reader.frame_rate().den)
    videoEncoder.video_time_base = videoFilter.time_base()
    videoEncoder.video_bit_rate = int(reader.bit_rate() / 100)

    # These settings can be used for hardware encoding if the host machine is configured
    #
    #videoEncoder.profile = "high"
    #videoEncoder.hw_video_codec_name = "h264_nvenc"
    #videoEncoder.hw_device_type = avio.AV_HWDEVICE_TYPE_CUDA
    #videoEncoder.hw_pix_fmt = avio.AV_PIX_FMT_CUDA
    #videoEncoder.sw_pix_fmt = avio.AV_PIX_FMT_YUV420P

    audioEncoder = avio.Encoder(writer, avio.AVMEDIA_TYPE_AUDIO)
    audioEncoder.set_audio_in(display.audio_out())
    audioEncoder.set_audio_out("apq_encoder")

    audioEncoder.set_channel_layout_stereo()
    audioEncoder.sample_fmt = avio.AV_SAMPLE_FMT_FLTP
    audioEncoder.audio_bit_rate = audioDecoder.bit_rate()
    audioEncoder.sample_rate = audioFilter.sample_rate()
    audioEncoder.audio_time_base = audioFilter.time_base()
    audioEncoder.channels = audioFilter.channels()
    audioEncoder.nb_samples = audioFilter.frame_size()

    process.add_reader(reader)
    process.add_decoder(videoDecoder)
    process.add_filter(videoFilter)
    process.add_encoder(videoEncoder)
    process.add_decoder(audioDecoder)
    process.add_filter(audioFilter)
    process.add_encoder(audioEncoder)
    process.add_display(display)

    process.run()    