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

#include "Exception.h"

namespace avio
{

enum class EncoderState {
    MIXED,
    OPEN,
    CLOSED
};

class Writer
{
public:
    Writer(const std::string& format);
    ~Writer();
    void open(const std::string& filename);
    void write(AVPacket* pkt);
    void close();
    void init();
    EncoderState getEncoderState();

    AVFormatContext* fmt_ctx = NULL;
    int video_stream_id = AVERROR_STREAM_NOT_FOUND;
    int audio_stream_id = AVERROR_STREAM_NOT_FOUND;

    std::string m_format;
    std::string write_dir;
    std::string filename;

    void* videoEncoder = nullptr;
    void* audioEncoder = nullptr;
    bool enabled = false;
    bool opened = false;

    bool show_video_pkts = false;
    bool show_audio_pkts = false;

    std::mutex mutex;

    ExceptionHandler ex;

};

}


