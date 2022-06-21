import avio
import argparse

from stats import Stats

class Player:

    def play(self, args):

        filename = eval(args.filename[0])

        vfilter = "null"
        if args.vfilter:
            vfilter = eval(args.vfilter)

        afilter = "anull"
        if args.afilter:
            afilter = eval(args.afilter)

        show_video = True
        if args.no_video:
            show_video = False

        show_audio = True
        if args.no_audio:
            show_audio = False

        pin_hud = False
        if args.pin_hud:
            pin_hud = True

        disable_hud = False
        if args.disable_hud:
            disable_hud = True

        hw_decode = False
        if args.hw_decode:
            hw_decode = True

        use_encoder = False
        if args.encode or args.hw_encode:
            use_encoder = True

        use_hw_encode = False
        if args.hw_encode:
            use_hw_encode = True

        encode_type = "mp4"
        if args.encode_type:
            encode_type = args.encode_type

        write_enable = False
        if args.write_enable:
            write_enable = True

        mobilenet = ""
        if args.mobilenet:
            mobilenet = eval(args.mobilenet)

        segment = False
        if args.segment:
            segment = True

        retinanet = False
        if args.retinanet:
            retinanet = True

        yolov5 = ""
        if args.yolov5:
            yolov5 = eval(args.yolov5)

        echo = ""
        if args.echo:
            echo = eval(args.echo)

        darknet = ""
        if args.darknet:
            darknet = eval(args.darknet)

        db_read = ""
        if args.db_read:
            db_read = eval(args.db_read)

        deep_sort = ""
        if args.deep_sort:
            deep_sort = eval(args.deep_sort)
    
        start_from = 0
        if args.start_from:
            start_from = args.start_from

        end_at = -1
        if args.end_at:
            end_at = args.end_at

        ignore_video_pts = False
        if args.ignore_video_pts:
            ignore_video_pts = True

        print(filename)
        reader = avio.Reader(filename)
        reader.start_from(start_from)
        if end_at > 0:
            reader.end_at(end_at)
        #reader.show_video_pkts = True

        display = avio.Display(reader)
        if pin_hud:
            display.pin_hud(True)
        if disable_hud:
            display.hud_enabled = False
        display.fix_audio_pop = False
        display.ignore_video_pts = ignore_video_pts
        display.prepend_recent_write = True
        #display.font_file = "/home/stephen/source/avio/avio/Roboto-Regular.ttf"
        process = avio.Process()
        process.add_reader(reader)

        if reader.has_video() and show_video:
            reader.set_video_out("vpq_reader")
            if filename == "pipe:":
                reader.vpq_max_size = 100
            if hw_decode:
                videoDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_VIDEO, avio.AV_HWDEVICE_TYPE_CUDA)
            else:
                videoDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_VIDEO)
            videoDecoder.set_video_in(reader.video_out())
            videoDecoder.set_video_out("vfq_decoder")
            videoFilter = avio.Filter(videoDecoder, vfilter)
            videoFilter.set_video_in(videoDecoder.video_out())
            videoFilter.set_video_out("vfq_filter")
            display.set_video_in(videoFilter.video_out())
            process.add_decoder(videoDecoder)
            process.add_filter(videoFilter)

        if reader.has_audio() and show_audio:
            reader.set_audio_out("apq_reader")
            if filename == "pipe:":
                reader.apq_max_size = 100
            audioDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_AUDIO)
            audioDecoder.set_audio_in(reader.audio_out())
            audioDecoder.set_audio_out("afq_decoder")
            audioFilter = avio.Filter(audioDecoder, afilter)
            audioFilter.set_audio_in(audioDecoder.audio_out())
            audioFilter.set_audio_out("afq_filter")
            display.set_audio_in(audioFilter.audio_out())
            display.sample_rate = audioFilter.sample_rate()
            display.channels = audioFilter.channels()
            display.channel_layout = audioFilter.channel_layout()
            display.sample_format = audioFilter.sample_format()
            display.frame_size = audioFilter.frame_size()
            display.audio_playback_format = avio.AV_SAMPLE_FMT_U8
            process.add_decoder(audioDecoder)
            process.add_filter(audioFilter)

        if use_encoder:
            writer = avio.Writer(encode_type)
            if args.output_filename:
                writer.filename = eval(args.output_filename)
            if args.output_dir:
                writer.write_dir = eval(args.output_dir)
            if write_enable:
                writer.enabled = True

            if reader.has_video() and show_video:
                display.set_video_out("vfq_display")
                videoEncoder = avio.Encoder(writer, avio.AVMEDIA_TYPE_VIDEO)
                videoEncoder.set_video_in(display.video_out())
                videoEncoder.set_video_out("vpq_encoder")
                #videoEncoder.frame_q_max_size = 200
                #videoEncoder.show_frames = True

                videoEncoder.pix_fmt = avio.AV_PIX_FMT_YUV420P
                videoEncoder.width = videoFilter.width()
                videoEncoder.height = videoFilter.height()
                videoEncoder.frame_rate = int(reader.frame_rate().num / reader.frame_rate().den)
                #videoEncoder.video_time_base.num = reader.frame_rate().den
                #videoEncoder.video_time_base.den = reader.frame_rate().num
                videoEncoder.video_time_base.num = 1
                videoEncoder.video_time_base.den = videoEncoder.frame_rate
                videoEncoder.video_bit_rate = int(videoDecoder.bit_rate()/4)
                videoEncoder.gop_size = 30
                #videoEncoder.profile = "high"
                #videoEncoder.show_frames = True
                if use_hw_encode:
                    videoEncoder.hw_video_codec_name = "h264_nvenc"
                    videoEncoder.hw_device_type = avio.AV_HWDEVICE_TYPE_CUDA
                    videoEncoder.hw_pix_fmt = avio.AV_PIX_FMT_CUDA
                    videoEncoder.sw_pix_fmt = avio.AV_PIX_FMT_YUV420P
                process.add_encoder(videoEncoder)

            if reader.has_audio() and show_audio:
                display.set_audio_out("afq_display")
                audioEncoder = avio.Encoder(writer, avio.AVMEDIA_TYPE_AUDIO)
                audioEncoder.set_audio_in(display.audio_out())
                audioEncoder.set_audio_out("apq_encoder")

                audioEncoder.set_channel_layout_stereo()
                audioEncoder.sample_fmt = avio.AV_SAMPLE_FMT_FLTP
                audioEncoder.audio_bit_rate = reader.audio_bit_rate()
                audioEncoder.sample_rate = reader.sample_rate()
                audioEncoder.audio_time_base.num = 1
                audioEncoder.audio_time_base.den = audioEncoder.sample_rate
                audioEncoder.channels = reader.channels()
                audioEncoder.nb_samples = reader.frame_size()
                #audioEncoder.show_frames = True
                process.add_encoder(audioEncoder)

        if len(darknet) > 0:
            process.set_python(display, "./darknet.py", "Darknet")
            process.set_python_init_arg(display, darknet)
        if len(echo) > 0:
            process.set_python(display, "./echo.py", "Echo")
            process.set_python_init_arg(display, echo)
        if len(db_read) > 0:
            process.set_python(display, "./db_reader.py", "DbReader")
            process.set_python_init_arg(display, db_read)
        if len(deep_sort) > 0:
            process.set_python(display, "./deep_sort/interface.py", "DeepSort")
            process.set_python_init_arg(display, deep_sort)
        if len(yolov5) > 0:
            process.set_python(display, "./yolov5.py", "YoloV5")
            process.set_python_init_arg(display, yolov5)
        if len(mobilenet) > 0:
            process.set_python(display, "./mobilenet.py", "Mobilenet")
            process.set_python_init_arg(display, mobilenet)
        if segment:
            process.set_python(display, "./segment/interface.py", "Segment")
        if retinanet:
            process.set_python(display, "./retinanet.py", "RetinaNet")
            
        process.add_display(display)
        process.run()
        print("python done")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="process media")
    parser.add_argument("filename", metavar="Filename", type=ascii, nargs="+", help="enter axis (x or y)")
    parser.add_argument("--vfilter", type=ascii)
    parser.add_argument("--afilter", type=ascii)
    parser.add_argument("--no_video", help="no video", action="store_true")
    parser.add_argument("--no_audio", help="no audio", action="store_true")
    parser.add_argument("--pin_hud", help="pin_hud", action="store_true")
    parser.add_argument("--disable_hud", help="disable_hud", action="store_true")
    parser.add_argument("--hw_decode", help="hw_decode", action="store_true")
    parser.add_argument("--encode", help="encode", action="store_true")
    parser.add_argument("--hw_encode", help="hw_encode", action="store_true")
    parser.add_argument("--encode_type", type=ascii)
    parser.add_argument("--output_filename", type=ascii)
    parser.add_argument("--output_dir", type=ascii)
    parser.add_argument("--write_enable", help="write_enable", action="store_true")
    parser.add_argument("--darknet", type=ascii, help="cfg=yolov4.cfg;weights=yolov4.weights;db_name=detect.db")
    parser.add_argument("--echo", type=ascii, help="key1=value1;key1=value2")
    parser.add_argument("--db_read", type=ascii, help="db_name=track.db")
    parser.add_argument("--deep_sort", type=ascii, help="model_name=./deep_sort/saved_model;gpu_mem_limit=6144;db_name_in=detect.db;db_name_out=track.db")
    parser.add_argument("--yolov5", type=ascii, help="repo=ultralytics/yolov5;model=yolov5x6;width=1920;height=1080")
    parser.add_argument("--mobilenet", type=ascii, help="model_name=C:/Users/sr996/Downloads/ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model;gpu_mem_limit=4096")
    parser.add_argument("--retinanet", help="RetinaNet", action="store_true")
    parser.add_argument("--segment", help="semantic segmentation", action="store_true")
    parser.add_argument("--ignore_video_pts", help="ignore video pts", action="store_true")
    parser.add_argument("--start_from", type=int)
    parser.add_argument("--end_at", type=int)
    args = parser.parse_args()

    player = Player()
    player.play(args)