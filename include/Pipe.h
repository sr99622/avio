#pragma once

extern "C" {
#include <libavutil/avassert.h>
#include <libavutil/channel_layout.h>
#include <libavutil/opt.h>
#include <libavutil/mathematics.h>
#include <libavutil/timestamp.h>
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>
#include <libswresample/swresample.h>
}

#include <mutex>

#include "Reader.h"
#include "Exception.h"

namespace avio
{

class Pipe
{
public:
    Pipe(Reader& reader, const std::string& filename);
    ~Pipe();

    AVCodecContext* getContext(AVMediaType mediaType);
    void open();
    void close();
    void write(AVPacket* pkt);

    std::string m_filename;
    Reader* reader;

    AVFormatContext* fmt_ctx = NULL;
    AVCodecContext* video_ctx = NULL;
    AVCodecContext* audio_ctx = NULL;
    AVStream* video_stream = NULL;
    AVStream* audio_stream = NULL;

    std::mutex mutex;

    std::string vpq_name;
    std::string apq_name;

    void set_video_in(const std::string& name) { vpq_name = std::string(name); }
    void set_audio_in(const std::string& name) { apq_name = std::string(name); }

    ExceptionHandler ex;

};

}


