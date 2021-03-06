#include "Pipe.h"

namespace avio
{

Pipe::Pipe(Reader& reader, const std::string& filename) : reader(&reader), m_filename(filename) 
{

}

Pipe::~Pipe()
{
    if (fmt_ctx) avformat_free_context(fmt_ctx);
    if (video_ctx) avcodec_free_context(&video_ctx);
}

AVCodecContext* Pipe::getContext(AVMediaType mediaType)
{
    AVCodecContext* dec_ctx = NULL;
    std::string strMediaType = "unknown";

    try {
        int stream_index = -1;

        if (mediaType == AVMEDIA_TYPE_VIDEO) {
            strMediaType = "video";
            stream_index = reader->video_stream_index;
        }
        else if (mediaType == AVMEDIA_TYPE_AUDIO) {
            strMediaType = "audio";
            stream_index = reader->audio_stream_index;
        }

        if (stream_index < 0) throw Exception("invalid stream index from reader");
        AVStream* stream = reader->fmt_ctx->streams[stream_index];
        const AVCodec* dec = avcodec_find_decoder(stream->codecpar->codec_id);
        if (!dec) throw Exception("could not find decoder");
        ex.ck(dec_ctx = avcodec_alloc_context3(dec), AAC3);
        ex.ck(avcodec_parameters_to_context(dec_ctx, stream->codecpar), APTC);
    }
    catch (const Exception& e) {
        std::cout << strMediaType << " Pipe::getContext exception: " << e.what() << std::endl;
    }

    return dec_ctx;
}

void Pipe::open()
{
    try {
        ex.ck(avformat_alloc_output_context2(&fmt_ctx, NULL, NULL, m_filename.c_str()), AAOC2);

        if (!vpq_name.empty()) {
            ex.ck(video_stream = avformat_new_stream(fmt_ctx, NULL), ANS);
            video_ctx = getContext(AVMEDIA_TYPE_VIDEO);
            if (video_ctx == NULL) throw Exception("no video reference context");
            ex.ck(avcodec_parameters_from_context(video_stream->codecpar, video_ctx), APFC);
            video_stream->time_base = reader->fmt_ctx->streams[reader->video_stream_index]->time_base;
        }

        if (!apq_name.empty()) {
            ex.ck(audio_stream = avformat_new_stream(fmt_ctx, NULL), ANS);
            audio_ctx = getContext(AVMEDIA_TYPE_AUDIO);
            if (audio_ctx == NULL) throw Exception("no audio reference context");
            ex.ck(avcodec_parameters_from_context(audio_stream->codecpar, audio_ctx), APFC);
            audio_stream->time_base = reader->fmt_ctx->streams[reader->audio_stream_index]->time_base;
        }

        ex.ck(avio_open(&fmt_ctx->pb, m_filename.c_str(), AVIO_FLAG_WRITE), AO);
        ex.ck(avformat_write_header(fmt_ctx, NULL), AWH);

        std::cout << "opened write file " << m_filename.c_str() << std::endl;
    }
    catch (const Exception& e) {
        std::cout << "Pipe::open exception: " << e.what() << std::endl;
    }
}

void Pipe::write(AVPacket* pkt)
{
    std::unique_lock<std::mutex> lock(mutex);
    try {
        ex.ck(av_interleaved_write_frame(fmt_ctx, pkt), AIWF);
    }
    catch (const Exception& e) {
        std::cout << "Pipe::write exception: " << e.what() << std::endl;
    }
}

void Pipe::close()
{
    try {
        ex.ck(av_write_trailer(fmt_ctx), AWT);
        ex.ck(avio_closep(&fmt_ctx->pb), ACP);
    }
    catch (const Exception& e) {
        std::cout << "Writer::close exception: " << e.what() << std::endl;
    }

    std::cout << "pipe closed file " << m_filename << std::endl;
}

}
