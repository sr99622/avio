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