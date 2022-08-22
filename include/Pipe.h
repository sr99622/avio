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
    Pipe(Reader& reader);
    ~Pipe();

    AVCodecContext* getContext(AVMediaType mediaType);
    void open(const std::string& filename);
    void close();
    void adjust_pts(AVPacket* pkt);
    void write(AVPacket* pkt);
    void show_ctx();

    std::string m_filename;
    Reader* reader;

    AVFormatContext* fmt_ctx = NULL;
    AVCodecContext* video_ctx = NULL;
    AVCodecContext* audio_ctx = NULL;
    AVStream* video_stream = NULL;
    AVStream* audio_stream = NULL;

    int64_t video_next_pts = 0;
    int64_t audio_next_pts = 0;
    int last_video_pkt_duration = 0;

    std::mutex mutex;

    ExceptionHandler ex;

};

}


