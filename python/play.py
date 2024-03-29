import argparse
import os
import warnings

import avio

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

        use_encoder = False
        if args.encode or args.hw_encode:
            use_encoder = True

        encode_type = "mp4"
        if args.encode_type:
            encode_type = args.encode_type

        retinanet = False
        if args.retinanet:
            retinanet = True

        bytetrack = ""
        if args.bytetrack:
            bytetrack = eval(args.bytetrack)

        detection = ""
        if args.detection:
            detection = eval(args.detection)

        segment = ""
        if args.segment:
            segment = eval(args.segment)

        keypoint = ""
        if args.keypoint:
            keypoint = eval(args.keypoint)
        
        yolov7 = ""
        if args.yolov7:
            yolov7 = eval(args.yolov7)

        yolov7_kpt = ""
        if args.yolov7_kpt:
            yolov7_kpt = eval(args.yolov7_kpt)

        mm_det = ""
        if args.mm_det:
            mm_det = eval(args.mm_det)

        mm_pose = ""
        if args.mm_pose:
            mm_pose = eval(args.mm_pose)
        
        mm_seg = ""
        if args.mm_seg:
            mm_seg = eval(args.mm_seg)

        harvest = ""
        if args.harvest:
            harvest = eval(args.harvest)

        echo = ""
        if args.echo:
            echo = eval(args.echo)

        darknet = ""
        if args.darknet:
            darknet = eval(args.darknet)

        db_read = ""
        if args.db_read:
            db_read = eval(args.db_read)

        start_from = 0
        if args.start_from:
            start_from = args.start_from

        end_at = -1
        if args.end_at:
            end_at = args.end_at

        read_q_size = 1
        if args.read_q_size:
            read_q_size = args.read_q_size

        print(filename)
        reader = avio.Reader(filename)
        reader.start_from(start_from)
        if end_at > 0:
            reader.end_at(end_at)

        if args.pipe_out:
            reader.pipe_out = True
            if args.output_filename:
                reader.pipe_out_filename = eval(args.output_filename)
            if args.output_dir:
                reader.pipe_out_dir = eval(args.output_dir)

        display = avio.Display(reader)
        if args.pin_osd:
            display.pin_osd(True)
        if args.disable_hud:
            display.osd_enabled = False
        if args.enable_status:
            display.enable_status(True)
        if args.ignore_video_pts:
            display.ignore_video_pts = True
        #if args.prepend_recent_write:
        #    display.prepend_recent_write = True
        if args.fullscreen:
            display.fullscreen = True
        if args.jpg_enabled:
            display.jpg_enabled = True

        process = avio.Process()
        process.add_reader(reader)

        if reader.has_video() and show_video:
            reader.set_video_out("vpq_reader")
            #if filename == "pipe:":
            reader.vpq_max_size = read_q_size
            if args.hw_decode:
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
            #reader.show_video_pkts = True
            #videoDecoder.show_frames = True

        if reader.has_audio() and show_audio:
            reader.set_audio_out("apq_reader")
            #if filename == "pipe:":
            reader.apq_max_size = read_q_size
            audioDecoder = avio.Decoder(reader, avio.AVMEDIA_TYPE_AUDIO)
            audioDecoder.set_audio_in(reader.audio_out())
            audioDecoder.set_audio_out("afq_decoder")
            audioFilter = avio.Filter(audioDecoder, afilter)
            audioFilter.set_audio_in(audioDecoder.audio_out())
            audioFilter.set_audio_out("afq_filter")
            display.set_audio_in(audioFilter.audio_out())
            #display.set_audio_in(audioDecoder.audio_out())
            display.audio_playback_format = avio.AV_SAMPLE_FMT_FLT
            process.add_decoder(audioDecoder)
            process.add_filter(audioFilter)
            #audioDecoder.show_frames = True
            #audioFilter.show_frames = True
            #reader.show_audio_pkts = True

        if use_encoder:
            writer = avio.Writer(encode_type)
            if args.output_filename:
                writer.filename = eval(args.output_filename)
            if args.output_dir:
                writer.write_dir = eval(args.output_dir)
            if args.write_enable:
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
                videoEncoder.profile = "high"
                #videoEncoder.show_frames = True
                if args.hw_encode:
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

                audioEncoder.set_channel_layout_mono()
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
        if retinanet:
            process.set_python(display, "./retinanet.py", "RetinaNet")
        if len(bytetrack) > 0:
            process.set_python(display, "./bytetrack/interface.py", "ByteTrack")
            process.set_python_init_arg(display, bytetrack)
        if len(detection) > 0:
            process.set_python(display, "./detectron2/detection.py", "Detection")
            process.set_python_init_arg(display, detection)
        if len(segment) > 0:
            process.set_python(display, "./detectron2/segment.py", "InstanceSegmentation")
            process.set_python_init_arg(display, segment)
        if len(keypoint) > 0:
            process.set_python(display, "./detectron2/keypoint.py", "Keypoint")
            process.set_python_init_arg(display, keypoint)
        if len(yolov7) > 0:
            process.set_python(display, "./yolov7/detection/detection.py", "Detection")
            process.set_python_init_arg(display, yolov7)
        if len(yolov7_kpt) > 0:
            process.set_python(display, "./yolov7/keypoint/keypoint.py", "Keypoint")
            process.set_python_init_arg(display, yolov7_kpt)
        if len(mm_det) > 0:
            process.set_python(display, "./mmlab/detection.py", "Detection")
            process.set_python_init_arg(display, mm_det)
        if len(mm_pose) > 0:
            process.set_python(display, "./mmlab/pose.py", "Pose")
            process.set_python_init_arg(display, mm_pose)
        if len(mm_seg) > 0:
            process.set_python(display, "./mmlab/segment.py", "Segment")
            process.set_python_init_arg(display, mm_seg)
        if len(harvest) > 0:
            process.set_python(display, "./harvest.py", "Harvest")
            process.set_python_init_arg(display, harvest)
        process.add_display(display)
        process.run()
        print("python done")
        
if __name__ == "__main__":

    warnings.filterwarnings("ignore", category=UserWarning)

    parser = argparse.ArgumentParser(description="process media")
    parser.add_argument("filename", metavar="Filename", type=ascii, nargs="+", help="media filename")
    parser.add_argument("--vfilter", type=ascii)
    parser.add_argument("--afilter", type=ascii)
    parser.add_argument("--no_video", help="no video", action="store_true")
    parser.add_argument("--no_audio", help="no audio", action="store_true")
    parser.add_argument("--pin_osd", help="pin_osd", action="store_true")
    parser.add_argument("--enable_status", help="enable_status", action="store_true")
    parser.add_argument("--disable_hud", help="disable_hud", action="store_true")
    parser.add_argument("--hw_decode", help="hw_decode", action="store_true")
    parser.add_argument("--encode", help="encode", action="store_true")
    parser.add_argument("--hw_encode", help="hw_encode", action="store_true")
    parser.add_argument("--pipe_out", help="enable pipe out for recording", action="store_true")
    parser.add_argument("--encode_type", type=ascii, help="encoder format name e.g. webm, mp4, avi, ...")
    parser.add_argument("--output_filename", type=ascii)
    parser.add_argument("--output_dir", type=ascii)
    parser.add_argument("--write_enable", help="write_enable", action="store_true")
    parser.add_argument("--darknet", type=ascii, help="cfg=yolov4.cfg;weights=yolov4.weights;db_name=detect.db")
    parser.add_argument("--echo", type=ascii, help="key1=value1,key1=value2")
    parser.add_argument("--db_read", type=ascii, help="db_name=track.db")
    parser.add_argument("--retinanet", help="RetinaNet", action="store_true")
    parser.add_argument("--detection", type=ascii, help="ckpt_file=auto,fp16=False,simple=False")
    parser.add_argument("--segment", type=ascii, help='ckpt_file=auto,fp16=True,overlay=False,simple=False')
    parser.add_argument("--keypoint", type=ascii, help='ckpt_file=auto,fp16=True,no_back=False,simple=False')
    parser.add_argument("--bytetrack", type=ascii, help="ckpt_file=bytetrack_l_mot17.pth.tar,fp16=True,force_cpu=True,trt_file=bytetrack_l_mot17_trt.pth")
    parser.add_argument("--yolov7", type=ascii, help="ckpt_file=auto")
    parser.add_argument("--yolov7_kpt", type=ascii, help="ckpt_file=auto")
    parser.add_argument("--mm_det", type=ascii, help="ckpt_file=auto")
    parser.add_argument("--mm_pose", type=ascii, help="ckpt_file=auto")
    parser.add_argument("--mm_seg", type=ascii, help="ckpt_file=auto")
    parser.add_argument("--ignore_video_pts", help="ignore video pts", action="store_true")
    parser.add_argument("--start_from", type=int, help="start the video at time in seconds")
    parser.add_argument("--end_at", type=int, help="stop the video at time in seconds")
    parser.add_argument("--read_q_size", type=int, help="reader max queue size in packets")
    parser.add_argument("--fullscreen", help="fullscreen", action="store_true")
    parser.add_argument("--jpg_enabled", help="enable jpg", action="store_true")
    parser.add_argument("--harvest", type=ascii, help="key=value")
    args = parser.parse_args()

    player = Player()
    player.play(args)