import avio
import os
import argparse

class Stats:
    def run(self, strFile):
        reader = avio.Reader(strFile)
        #reader.set_video_out("vpq_reader")
        #reader.set_audio_out("apq_reader")

        seconds = int((reader.duration()/1000)%60)
        minutes = int((reader.duration()/(1000*60))%60)
        print("\nFile:", strFile)
        if not strFile == "pipe:":
            print("Size:", "{:.2f}".format(os.stat(strFile).st_size / (1024 * 1024)), "Megabytes")
        print("\nMedia start time:", "{:.3f}".format(float(reader.start_time()/ 1000)))
        print("Media Duration:  ", str(minutes) + ":" + "{:02d}".format(seconds))
        if (reader.has_video()):
            print("\nVideo")
            print("  width:          ", reader.width())
            print("  height:         ", reader.height())
            print("  pixel format:   ", reader.str_pix_fmt())
            print("  video codec:    ", reader.str_video_codec())
            print("  video bit rate: ", reader.video_bit_rate())
            fps =  "{:.2f}".format(reader.frame_rate().num/reader.frame_rate().den)
            print("  frame rate:     ", reader.frame_rate().num, "/", reader.frame_rate().den, ", fps =", fps)
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

        #reader.close()

class Packets:
    def run(self, strFile, video, audio):
        process = avio.Process()
        reader = avio.Reader(strFile)

        if reader.has_video():
            reader.set_video_out("vpq_reader")
            reader.show_video_pkts = video
            process.add_packet_drain(reader.video_out())

        if reader.has_audio():
            reader.set_audio_out("apq_reader")
            reader.show_audio_pkts = audio
            process.add_packet_drain(reader.audio_out())

        process.add_reader(reader)
        process.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show media file stats")
    parser.add_argument("filename", metavar="Filename", type=ascii, nargs="+")
    parser.add_argument("--show", help="show", action="store_true")
    args = parser.parse_args()
    strFile = eval(args.filename[0])
    if args.show:
        packets = Packets()
        packets.run(strFile, True, True)
    else:
        stats = Stats()
        stats.run(strFile)