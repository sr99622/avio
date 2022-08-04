#include "numpy_init.h"
#include <iostream>
#include <filesystem>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Factory.h" 
#include "Display.h"

#define VERSION_INFO "1.0.0"

namespace py = pybind11;

namespace avio
{

typedef std::map<std::string, Queue<AVPacket*>*> PKT_Q_MAP;
typedef std::map<std::string, Queue<Frame>*> FRAME_Q_MAP;
    
class Process
{
public:

    Reader*   reader       = nullptr;
    Decoder*  videoDecoder = nullptr;
    Decoder*  audioDecoder = nullptr;
    Filter*   videoFilter  = nullptr;
    Filter*   audioFilter  = nullptr;
    Writer*   writer       = nullptr;
    Encoder*  videoEncoder = nullptr;
    Encoder*  audioEncoder = nullptr;
    Display*  display      = nullptr;

    PKT_Q_MAP pkt_queues;
    FRAME_Q_MAP frame_queues;
    std::vector<std::string> pkt_q_names;
    std::vector<std::string> frame_q_names;
    std::map<std::string, std::string> display_q_names;
    std::vector<std::string> frame_q_drain_names;
    std::vector<std::string> pkt_q_drain_names;
    std::vector<std::string> merge_filenames;
    
    int interleaved_q_size = 0;
    std::string interleaved_q_name;
    bool muxing = false;
    std::string mux_video_q_name;
    std::string mux_audio_q_name;

    std::vector<std::thread*> ops;

    void trim(const std::string& in, const std::string& out, int64_t start, int64_t end)
    {
        int64_t video_next_pts = 0;
        int64_t audio_next_pts = 0;

        Reader reader(in.c_str());
        if (start > 0) reader.start_from(start);
        if (end > 0) reader.end_at(end);
        Pipe pipe(reader, out.c_str());
        if (reader.has_video()) pipe.set_video_in("dummy");
        if (reader.has_audio()) pipe.set_audio_in("dummy");
        pipe.open();

        while (AVPacket* pkt = reader.read()) {

            if (reader.seek_target_pts != AV_NOPTS_VALUE) {
                av_packet_free(&pkt);
                pkt = reader.seek();
                if (!pkt) {
                    break;
                }
            }

            if (reader.stop_play_at_pts != AV_NOPTS_VALUE && pkt->stream_index == reader.seek_stream_index()) {
                if (pkt->pts > reader.stop_play_at_pts) {
                    av_packet_free(&pkt);
                    break;
                }
            }

            if (pkt->stream_index == reader.video_stream_index) {
                pkt->stream_index = pipe.video_stream->index;
                pkt->dts = pkt->pts = video_next_pts;
                video_next_pts += pkt->duration;
            }

            else if (pkt->stream_index == reader.audio_stream_index) {
                pkt->stream_index = pipe.audio_stream->index;
                pkt->dts = pkt->pts = audio_next_pts;
                audio_next_pts += pkt->duration;
            }
            
            pipe.write(pkt);
            av_packet_free(&pkt);

        }
        pipe.close();
    }

    void merge(const std::string& out_filename)
    {
        Pipe* pipe = nullptr;

        int64_t video_next_pts = 0;
        int64_t audio_next_pts = 0;

        for (const std::string filename : merge_filenames) {
            Reader reader(filename.c_str());
            std::cout << "merging " << filename << " into " << out_filename << std::endl;
            if (!pipe) {
                pipe = new Pipe(reader, out_filename);
                if (reader.has_video()) pipe->set_video_in("dummy");
                if (reader.has_audio()) pipe->set_audio_in("dummy");
                pipe->open();
            }

            while (AVPacket* pkt = reader.read()) {

                if (pkt->stream_index == reader.video_stream_index) {
                    pkt->stream_index = pipe->video_stream->index;
                    pkt->dts = pkt->pts = video_next_pts;
                    video_next_pts += pkt->duration;
                }
                else if (pkt->stream_index == reader.audio_stream_index) {
                    pkt->stream_index = pipe->audio_stream->index;
                    pkt->dts = pkt->pts = audio_next_pts;
                    audio_next_pts += pkt->duration;
                }

                pipe->write(pkt);
                av_packet_free(&pkt);
            }
        }

        if (pipe) {
            pipe->close();
            delete pipe;
        }
    }

    void add_reader(Reader& reader_in)
    {
        reader = &reader_in;
        if (!reader_in.vpq_name.empty()) pkt_q_names.push_back(reader_in.vpq_name);
        if (!reader_in.apq_name.empty()) pkt_q_names.push_back(reader_in.apq_name);
    }

    void add_decoder(Decoder& decoder_in)
    {
        if (decoder_in.mediaType == AVMEDIA_TYPE_VIDEO)
            videoDecoder = &decoder_in;
        if (decoder_in.mediaType == AVMEDIA_TYPE_AUDIO)
            audioDecoder = &decoder_in;

        pkt_q_names.push_back(decoder_in.pkt_q_name);
        frame_q_names.push_back(decoder_in.frame_q_name);
    }

    void add_filter(Filter& filter_in)
    {
        if (filter_in.mediaType() == AVMEDIA_TYPE_VIDEO)
            videoFilter = &filter_in;
        if (filter_in.mediaType() == AVMEDIA_TYPE_AUDIO)
            audioFilter = &filter_in;

        frame_q_names.push_back(filter_in.q_in_name);
        frame_q_names.push_back(filter_in.q_out_name);
    }

    void add_encoder(Encoder& encoder_in)
    {
        if (encoder_in.mediaType == AVMEDIA_TYPE_VIDEO) {
            videoEncoder = &encoder_in;
            writer = videoEncoder->writer;
        }
        if (encoder_in.mediaType == AVMEDIA_TYPE_AUDIO) {
            audioEncoder = &encoder_in;
            writer = audioEncoder->writer;
        }
        pkt_q_names.push_back(encoder_in.pkt_q_name);
        frame_q_names.push_back(encoder_in.frame_q_name);
    }

    void add_frame_drain(const std::string& frame_q_name)
    {
        frame_q_drain_names.push_back(frame_q_name);
    }

    void add_packet_drain(const std::string& pkt_q_name)
    {
        pkt_q_drain_names.push_back(pkt_q_name);
    }

    void add_display(Display& display_in)
    {
        display = &display_in;
        //display->init();

        if (!display->vfq_out_name.empty())
            frame_q_names.push_back(display->vfq_out_name);
        if (!display->afq_out_name.empty())
            frame_q_names.push_back(display->afq_out_name);
    }

    int set_python(Display& display_in, const std::string& python_file_path, const std::string& python_class)
    {
        std::filesystem::path path(python_file_path);

        display_in.pythonDir = path.parent_path().string();
        display_in.pythonFile = path.stem().string();
        display_in.pythonClass = python_class;

        import_array();
        if (PyErr_Occurred())
            std::cout << "Failed to import numpy" << std::endl;

        return 0;
    }

    void set_python_init_arg(Display& display_in, const std::string& arg)
    {
        display_in.pythonInitArg = arg;
    }

    void run()
    {
        av_log_set_level(AV_LOG_PANIC);        

        for (const std::string& name : pkt_q_names) {
            if (!name.empty()) {
                if (pkt_queues.find(name) == pkt_queues.end())
                    pkt_queues.insert({ name, new Queue<AVPacket*>() });
            }
        }

        for (const std::string& name : frame_q_names) {
            if (!name.empty()) {
                if (frame_queues.find(name) == frame_queues.end())
                    frame_queues.insert({ name, new Queue<Frame>() });
            }
        }

        if (reader) {
            ops.push_back(new std::thread(read, reader,
                reader->has_video() ? pkt_queues[reader->vpq_name] : nullptr, 
                reader->has_audio() ? pkt_queues[reader->apq_name] : nullptr));
        }

        if (videoDecoder) {
            ops.push_back(new std::thread(decode, videoDecoder,
                pkt_queues[videoDecoder->pkt_q_name], frame_queues[videoDecoder->frame_q_name]));
        }

        if (audioDecoder) {
            ops.push_back(new std::thread(decode, audioDecoder,
                pkt_queues[audioDecoder->pkt_q_name], frame_queues[audioDecoder->frame_q_name]));
        }

        if (videoFilter) {
            ops.push_back(new std::thread(filter, videoFilter,
                frame_queues[videoFilter->q_in_name], frame_queues[videoFilter->q_out_name]));
        }

        if (audioFilter) {
            ops.push_back(new std::thread(filter, audioFilter,
                frame_queues[audioFilter->q_in_name], frame_queues[audioFilter->q_out_name]));
        }

        if (videoEncoder) {
            videoEncoder->pkt_q = pkt_queues[videoEncoder->pkt_q_name];
            videoEncoder->frame_q = frame_queues[videoEncoder->frame_q_name];
            if (videoEncoder->frame_q_max_size > 0) videoEncoder->frame_q->set_max_size(videoEncoder->frame_q_max_size);
            if (writer->enabled) videoEncoder->init();
            ops.push_back(new std::thread(write, videoEncoder->writer, videoEncoder));
        }

        if (audioEncoder) {
            audioEncoder->pkt_q = pkt_queues[audioEncoder->pkt_q_name];
            audioEncoder->frame_q = frame_queues[audioEncoder->frame_q_name];
            if (audioEncoder->frame_q_max_size > 0) audioEncoder->frame_q->set_max_size(audioEncoder->frame_q_max_size);
            if (writer->enabled) audioEncoder->init();
            ops.push_back(new std::thread(write, audioEncoder->writer, audioEncoder));
        }

        for (const std::string& name : frame_q_drain_names)
            ops.push_back(new std::thread(frame_drain, frame_queues[name]));

        for (const std::string& name : pkt_q_drain_names)
            ops.push_back(new std::thread(pkt_drain, pkt_queues[name]));

        if (display) {

            if (writer) display->writer = writer;
            if (audioDecoder) display->audioDecoder = audioDecoder;
            if (audioFilter) display->audioFilter = audioFilter;

            if (!display->vfq_in_name.empty()) display->vfq_in = frame_queues[display->vfq_in_name];
            if (!display->afq_in_name.empty()) display->afq_in = frame_queues[display->afq_in_name];

            if (!display->vfq_out_name.empty()) display->vfq_out = frame_queues[display->vfq_out_name];
            if (!display->afq_out_name.empty()) display->afq_out = frame_queues[display->afq_out_name];

            display->init();
            while (display->display()) {}

            if (writer) {
                while (!display->audio_eof)
                    SDL_Delay(1);
                writer->enabled = false;
            }

            for (PKT_Q_MAP::iterator q = pkt_queues.begin(); q != pkt_queues.end(); ++q) {
                if (!q->first.empty()) {
                    q->second->close();
                    delete q->second;
                }
            }

            for (FRAME_Q_MAP::iterator q = frame_queues.begin(); q != frame_queues.end(); ++q) {
                if (!q->first.empty()) {
                    q->second->close();
                    delete q->second;
                }
            }
        }

        for (int i = 0; i < ops.size(); i++) {
            ops[i]->join();
            delete ops[i];
        }

        std::exit(0);
    }
};

PYBIND11_MODULE(avio, m)
{
    m.doc() = "pybind11 av plugin";
    py::class_<Process>(m, "Process")
        .def(py::init<>())
        .def("add_reader", &Process::add_reader)
        .def("add_decoder", &Process::add_decoder)
        .def("add_filter", &Process::add_filter)
        .def("add_display", &Process::add_display)
        .def("add_encoder", &Process::add_encoder)
        .def("set_python", &Process::set_python)
        .def("set_python_init_arg", &Process::set_python_init_arg)
        .def("merge", &Process::merge)
        .def("trim", &Process::trim)
        .def("run", &Process::run)
        .def("add_frame_drain", &Process::add_frame_drain)
        .def("add_packet_drain", &Process::add_packet_drain)
        .def_readwrite("merge_filenames", &Process::merge_filenames);
    py::class_<Reader>(m, "Reader")
        .def(py::init<const char*>())
        .def("start_time", &Reader::start_time)
        .def("duration", &Reader::duration)
        .def("bit_rate", &Reader::bit_rate)
        .def("has_video", &Reader::has_video)
        .def("width", &Reader::width)
        .def("height", &Reader::height)
        .def("frame_rate", &Reader::frame_rate)
        .def("pix_fmt", &Reader::pix_fmt)
        .def("str_pix_fmt", &Reader::str_pix_fmt)
        .def("video_codec", &Reader::video_codec)
        .def("str_video_codec", &Reader::str_video_codec)
        .def("video_bit_rate", &Reader::video_bit_rate)
        .def("video_time_base", &Reader::video_time_base)
        .def("has_audio", &Reader::has_audio)
        .def("channels", &Reader::channels)
        .def("sample_rate", &Reader::sample_rate)
        .def("frame_size", &Reader::frame_size)
        .def("channel_layout", &Reader::channel_layout)
        .def("str_channel_layout", &Reader::str_channel_layout)
        .def("sample_format", &Reader::sample_format)
        .def("str_sample_format", &Reader::str_sample_format)
        .def("audio_codec", &Reader::audio_codec)
        .def("str_audio_codec", &Reader::str_audio_codec)
        .def("audio_bit_rate", &Reader::audio_bit_rate)
        .def("audio_time_base", &Reader::audio_time_base)
        .def("video_out", &Reader::video_out)
        .def("audio_out", &Reader::audio_out)
        .def("set_video_out", &Reader::set_video_out)
        .def("set_audio_out", &Reader::set_audio_out)
        .def("request_seek", &Reader::request_seek)
        .def("start_from", &Reader::start_from)
        .def("end_at", &Reader::end_at)
        .def_readwrite("vpq_max_size", &Reader::vpq_max_size)
        .def_readwrite("apq_max_size", &Reader::apq_max_size)
        .def_readwrite("show_video_pkts", &Reader::show_video_pkts)
        .def_readwrite("show_audio_pkts", &Reader::show_audio_pkts)
        .def_readwrite("vpq_name", &Reader::vpq_name)
        .def_readwrite("apq_name", &Reader::apq_name);
    py::class_<Decoder>(m, "Decoder")
        .def(py::init<Reader&, AVMediaType>())
        .def(py::init<Reader&, AVMediaType, AVHWDeviceType>())
        .def("sample_rate", &Decoder::sample_rate)
        .def("channels", &Decoder::channels)
        .def("frame_size", &Decoder::frame_size)
        .def("channel_layout", &Decoder::channel_layout)
        .def("sample_format", &Decoder::sample_format)
        .def("bit_rate", &Decoder::bit_rate)
        .def("width", &Decoder::width)
        .def("height", &Decoder::height)
        .def("pix_fmt", &Decoder::pix_fmt)
        .def("nb_frames", &Decoder::nb_frames)
        .def("duration", &Decoder::duration)
        .def("time_base", &Decoder::time_base)
        .def("video_in", &Decoder::video_in)
        .def("audio_in", &Decoder::audio_in)
        .def("video_out", &Decoder::video_out)
        .def("audio_out", &Decoder::audio_out)
        .def("set_video_in", &Decoder::set_video_in)
        .def("set_audio_in", &Decoder::set_audio_in)
        .def("set_video_out", &Decoder::set_video_out)
        .def("set_audio_out", &Decoder::set_audio_out)
        .def_readwrite("show_frames", &Decoder::show_frames)
        .def_readwrite("frame_q_name", &Decoder::frame_q_name)
        .def_readwrite("pkt_q_name", &Decoder::pkt_q_name);
    py::class_<Filter>(m, "Filter")
        .def(py::init<Decoder&, const char*>())
        .def("width", &Filter::width)
        .def("height", &Filter::height)
        .def("pix_fmt", &Filter::pix_fmt)
        .def("time_base", &Filter::time_base)
        .def("frame_rate", &Filter::frame_rate)
        .def("sample_rate", &Filter::sample_rate)
        .def("channels", &Filter::channels)
        .def("channel_layout", &Filter::channel_layout)
        .def("sample_format", &Filter::sample_format)
        .def("frame_size", &Filter::frame_size)
        .def("video_in", &Filter::video_in)
        .def("video_out", &Filter::video_out)
        .def("set_video_in", &Filter::set_video_in)
        .def("set_video_out", &Filter::set_video_out)
        .def("audio_in", &Filter::audio_in)
        .def("audio_out", &Filter::audio_out)
        .def("set_audio_in", &Filter::set_audio_in)
        .def("set_audio_out", &Filter::set_audio_out)
        .def_readwrite("q_in_name", &Filter::q_in_name)
        .def_readwrite("q_out_name", &Filter::q_out_name);
    py::class_<Display>(m, "Display")
        .def(py::init<Reader&>())
        .def("initVideo", &Display::initVideo)
        .def("pin_osd", &Display::pin_osd)
        .def("enable_status", &Display::enable_status)
        .def("video_in", &Display::video_in)
        .def("audio_in", &Display::audio_in)
        .def("video_out", &Display::video_out)
        .def("audio_out", &Display::audio_out)
        .def("set_video_in", &Display::set_video_in)
        .def("set_audio_in", &Display::set_audio_in)
        .def("set_video_out", &Display::set_video_out)
        .def("set_audio_out", &Display::set_audio_out)
        .def_readwrite("vfq_in_name", &Display::vfq_in_name)
        .def_readwrite("afq_in_name", &Display::afq_in_name)
        .def_readwrite("vfq_out_name", &Display::vfq_out_name)
        .def_readwrite("afq_out_name", &Display::afq_out_name)
        .def_readwrite("audio_playback_format", &Display::sdl_sample_format)
        .def_readwrite("disable_audio", &Display::disable_audio)
        .def_readwrite("osd_enabled", &Display::osd_enabled)
        .def_readwrite("ignore_video_pts", &Display::ignore_video_pts)
        .def_readwrite("recent_q_size", &Display::recent_q_size)
        .def_readwrite("prepend_recent_write", &Display::prepend_recent_write)
        .def_readwrite("font_file", &Display::font_file)
        .def_readwrite("start_time", &Display::start_time)
        .def_readwrite("duration", &Display::duration)
        .def_readwrite("width", &Display::width)
        .def_readwrite("height", &Display::height)
        .def_readwrite("pix_fmt", &Display::pix_fmt);
    py::class_<Writer>(m, "Writer")
        .def(py::init<const std::string&>())
        .def_readwrite("enabled", &Writer::enabled)
        .def_readwrite("write_dir", &Writer::write_dir)
        .def_readwrite("filename", &Writer::filename)
        .def_readwrite("show_video_pkts", &Writer::show_video_pkts)
        .def_readwrite("show_audio_pkts", &Writer::show_audio_pkts);
    py::class_<Pipe>(m, "Pipe")
        .def(py::init<Reader&, const std::string&>())
        .def("set_video_in", &Pipe::set_video_in)
        .def("set_audio_in", &Pipe::set_audio_in)
        .def_readwrite("vpq_name", &Pipe::vpq_name)
        .def_readwrite("apq_name", &Pipe::apq_name);
    py::class_<Encoder>(m, "Encoder")
        .def(py::init<Writer&, AVMediaType>())
        .def("video_in", &Encoder::video_in)
        .def("audio_in", &Encoder::audio_in)
        .def("video_out", &Encoder::video_out)
        .def("audio_out", &Encoder::audio_out)
        .def("set_video_in", &Encoder::set_video_in)
        .def("set_audio_in", &Encoder::set_audio_in)
        .def("set_video_out", &Encoder::set_video_out)
        .def("set_audio_out", &Encoder::set_audio_out)
        .def("set_channel_layout_mono", &Encoder::set_channel_layout_mono)
        .def("set_channel_layout_stereo", &Encoder::set_channel_layout_stereo)
        .def_readwrite("pix_fmt", &Encoder::pix_fmt)
        .def_readwrite("width", &Encoder::width)
        .def_readwrite("height", &Encoder::height)
        .def_readwrite("video_bit_rate", &Encoder::video_bit_rate)
        .def_readwrite("frame_rate", &Encoder::frame_rate)
        .def_readwrite("gop_size", &Encoder::gop_size)
        .def_readwrite("video_time_base", &Encoder::video_time_base)
        .def_readwrite("profile", &Encoder::profile)
        .def_readwrite("hw_video_codec_name", &Encoder::hw_video_codec_name)
        .def_readwrite("hw_device_type", &Encoder::hw_device_type)
        .def_readwrite("hw_pix_fmt", &Encoder::hw_pix_fmt)
        .def_readwrite("sw_pix_fmt", &Encoder::sw_pix_fmt)
        .def_readwrite("sample_fmt", &Encoder::sample_fmt)
        .def_readwrite("channel_layout", &Encoder::channel_layout)
        .def_readwrite("audio_bit_rate", &Encoder::audio_bit_rate)
        .def_readwrite("sample_rate", &Encoder::sample_rate)
        .def_readwrite("nb_samples", &Encoder::nb_samples)
        .def_readwrite("channels", &Encoder::channels)
        .def_readwrite("audio_time_base", &Encoder::audio_time_base)
        .def_readwrite("show_frames", &Encoder::show_frames)
        .def_readwrite("frame_q_max_size", &Encoder::frame_q_max_size)
        .def_readwrite("pkt_q_name", &Encoder::pkt_q_name)
        .def_readwrite("frame_q_name", &Encoder::frame_q_name);
    py::class_<AVRational>(m, "AVRational")
        .def(py::init<>())
        .def_readwrite("num", &AVRational::num)
        .def_readwrite("den", &AVRational::den);
    py::enum_<AVMediaType>(m, "AVMediaType")
        .value("AVMEDIA_TYPE_UNKNOWN", AVMediaType::AVMEDIA_TYPE_UNKNOWN)
        .value("AVMEDIA_TYPE_VIDEO", AVMediaType::AVMEDIA_TYPE_VIDEO)
        .value("AVMEDIA_TYPE_AUDIO", AVMediaType::AVMEDIA_TYPE_AUDIO)
        .export_values();
    py::enum_<AVPixelFormat>(m, "AVPixelFormat")
        .value("AV_PIX_FMT_NONE", AVPixelFormat::AV_PIX_FMT_NONE)
        .value("AV_PIX_FMT_YUV420P", AVPixelFormat::AV_PIX_FMT_YUV420P)
        .value("AV_PIX_FMT_RGB24", AVPixelFormat::AV_PIX_FMT_RGB24)
        .value("AV_PIX_FMT_BGR24", AVPixelFormat::AV_PIX_FMT_BGR24)
        .value("AV_PIX_FMT_NV12", AVPixelFormat::AV_PIX_FMT_NV12)
        .value("AV_PIX_FMT_NV21", AVPixelFormat::AV_PIX_FMT_NV21)
        .value("AV_PIX_FMT_RGBA", AVPixelFormat::AV_PIX_FMT_RGBA)
        .value("AV_PIX_FMT_BGRA", AVPixelFormat::AV_PIX_FMT_BGRA)
        .value("AV_PIX_FMT_VAAPI", AVPixelFormat::AV_PIX_FMT_VAAPI)
        .value("AV_PIX_FMT_CUDA", AVPixelFormat::AV_PIX_FMT_CUDA)
        .value("AV_PIX_FMT_QSV", AVPixelFormat::AV_PIX_FMT_QSV)
        .value("AV_PIX_FMT_D3D11VA_VLD", AVPixelFormat::AV_PIX_FMT_D3D11VA_VLD)
        .value("AV_PIX_FMT_VDPAU", AVPixelFormat::AV_PIX_FMT_VDPAU)
        .value("AV_PIX_FMT_D3D11", AVPixelFormat::AV_PIX_FMT_D3D11)
        .value("AV_PIX_FMT_OPENCL", AVPixelFormat::AV_PIX_FMT_OPENCL)
        .value("AV_PIX_FMT_GRAY8", AVPixelFormat::AV_PIX_FMT_GRAY8)
        .export_values();
    py::enum_<AVHWDeviceType>(m, "AVHWDeviceType")
        .value("AV_HWDEVICE_TYPE_NONE", AVHWDeviceType::AV_HWDEVICE_TYPE_NONE)
        .value("AV_HWDEVICE_TYPE_VDPAU", AVHWDeviceType::AV_HWDEVICE_TYPE_VDPAU)
        .value("AV_HWDEVICE_TYPE_CUDA", AVHWDeviceType::AV_HWDEVICE_TYPE_CUDA)
        .value("AV_HWDEVICE_TYPE_VAAPI", AVHWDeviceType::AV_HWDEVICE_TYPE_VAAPI)
        .value("AV_HWDEVICE_TYPE_DXVA2", AVHWDeviceType::AV_HWDEVICE_TYPE_DXVA2)
        .value("AV_HWDEVICE_TYPE_QSV", AVHWDeviceType::AV_HWDEVICE_TYPE_QSV)
        .value("AV_HWDEVICE_TYPE_VIDEOTOOLBOX", AVHWDeviceType::AV_HWDEVICE_TYPE_VIDEOTOOLBOX)
        .value("AV_HWDEVICE_TYPE_D3D11VA", AVHWDeviceType::AV_HWDEVICE_TYPE_D3D11VA)
        .value("AV_HWDEVICE_TYPE_DRM", AVHWDeviceType::AV_HWDEVICE_TYPE_DRM)
        .value("AV_HWDEVICE_TYPE_OPENCL", AVHWDeviceType::AV_HWDEVICE_TYPE_OPENCL)
        .value("AV_HWDEVICE_TYPE_MEDIACODEC", AVHWDeviceType::AV_HWDEVICE_TYPE_MEDIACODEC)
        .export_values();
    py::enum_<AVSampleFormat>(m, "AVSampleFormat")
        .value("AV_SAMPLE_FMT_NONE", AVSampleFormat::AV_SAMPLE_FMT_NONE)
        .value("AV_SAMPLE_FMT_U8", AVSampleFormat::AV_SAMPLE_FMT_U8)
        .value("AV_SAMPLE_FMT_S16", AVSampleFormat::AV_SAMPLE_FMT_S16)
        .value("AV_SAMPLE_FMT_S32", AVSampleFormat::AV_SAMPLE_FMT_S32)
        .value("AV_SAMPLE_FMT_FLT", AVSampleFormat::AV_SAMPLE_FMT_FLT)
        .value("AV_SAMPLE_FMT_DBL", AVSampleFormat::AV_SAMPLE_FMT_DBL)
        .value("AV_SAMPLE_FMT_U8P", AVSampleFormat::AV_SAMPLE_FMT_U8P)
        .value("AV_SAMPLE_FMT_S16P", AVSampleFormat::AV_SAMPLE_FMT_S16P)
        .value("AV_SAMPLE_FMT_S32P", AVSampleFormat::AV_SAMPLE_FMT_S32P)
        .value("AV_SAMPLE_FMT_FLTP", AVSampleFormat::AV_SAMPLE_FMT_FLTP)
        .value("AV_SAMPLE_FMT_DBLP", AVSampleFormat::AV_SAMPLE_FMT_DBLP)
        .value("AV_SAMPLE_FMT_S64", AVSampleFormat::AV_SAMPLE_FMT_S64)
        .value("AV_SAMPLE_FMT_S64P", AVSampleFormat::AV_SAMPLE_FMT_S64P)
        .value("AV_SAMPLE_FMT_NB", AVSampleFormat::AV_SAMPLE_FMT_NB)
        .export_values();

    #ifdef VERSION_INFO
        m.attr("__version__") = VERSION_INFO;
    #else
        m.attr("__version__") = "dev";
    #endif

}

}
