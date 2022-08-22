#include "Pipe.h"

namespace avio
{

Pipe::Pipe(Reader& reader) : reader(&reader)
{

}

Pipe::~Pipe()
{
    if (fmt_ctx) avformat_free_context(fmt_ctx);
    if (video_ctx) avcodec_free_context(&video_ctx);
}

AVCodecContext* Pipe::getContext(AVMediaType mediaType)
{
    AVCodecContext* enc_ctx = NULL;
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
        const AVCodec* enc = avcodec_find_encoder(stream->codecpar->codec_id);
        if (!enc) throw Exception("could not find encoder");
        ex.ck(enc_ctx = avcodec_alloc_context3(enc), AAC3);
        ex.ck(avcodec_parameters_to_context(enc_ctx, stream->codecpar), APTC);
    }
    catch (const Exception& e) {
        std::cout << strMediaType << " Pipe::getContext exception: " << e.what() << std::endl;
    }

    return enc_ctx;
}

void Pipe::open(const std::string& filename)
{
    try {
        ex.ck(avformat_alloc_output_context2(&fmt_ctx, NULL, NULL, filename.c_str()), AAOC2);

        ex.ck(video_stream = avformat_new_stream(fmt_ctx, NULL), ANS);
        video_ctx = getContext(AVMEDIA_TYPE_VIDEO);
        if (video_ctx == NULL) throw Exception("no video reference context");
        ex.ck(avcodec_parameters_from_context(video_stream->codecpar, video_ctx), APFC);
        video_stream->time_base = reader->fmt_ctx->streams[reader->video_stream_index]->time_base;

        ex.ck(audio_stream = avformat_new_stream(fmt_ctx, NULL), ANS);
        audio_ctx = getContext(AVMEDIA_TYPE_AUDIO);
        if (audio_ctx == NULL) throw Exception("no audio reference context");
        ex.ck(avcodec_parameters_from_context(audio_stream->codecpar, audio_ctx), APFC);
        audio_stream->time_base = reader->fmt_ctx->streams[reader->audio_stream_index]->time_base;

        show_ctx();
        ex.ck(avio_open(&fmt_ctx->pb, filename.c_str(), AVIO_FLAG_WRITE), AO);
        ex.ck(avformat_write_header(fmt_ctx, NULL), AWH);

        video_next_pts = 0;
        audio_next_pts = 0;

        std::cout << "opened write file " << filename.c_str() << std::endl;
    }
    catch (const Exception& e) {
        std::cout << "Pipe::open exception: " << e.what() << std::endl;
    }
}

void Pipe::adjust_pts(AVPacket* pkt)
{
    if (pkt->stream_index == reader->video_stream_index) {
        pkt->stream_index = video_stream->index;
        pkt->dts = pkt->pts = video_next_pts;
        video_next_pts += pkt->duration;
    }
    else if (pkt->stream_index == reader->audio_stream_index) {
        pkt->stream_index = audio_stream->index;
        pkt->dts = pkt->pts = audio_next_pts;
        audio_next_pts += pkt->duration;
    }
}

void Pipe::write(AVPacket* pkt)
{
    adjust_pts(pkt);
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

    //std::cout << "pipe closed file " << filename << std::endl;
}

void Pipe::show_ctx()
{
    for (int i = 0; i < fmt_ctx->nb_streams; i++) {
        AVStream* stream = fmt_ctx->streams[i];
        enum AVMediaType media_type = stream->codecpar->codec_type;
        switch (media_type) {
            case AVMEDIA_TYPE_VIDEO:
                std::cout << "Video Stream" << std::endl;
                break;
            case AVMEDIA_TYPE_AUDIO:
                std::cout << "Audio Stream" << std::endl;
                std::cout << "sample rate:       " << stream->codecpar->sample_rate << std::endl;
                std::cout << "sample channels:   " << stream->codecpar->channels << std::endl;
                std::cout << "sample frame_size: " << stream->codecpar->frame_size << std::endl;
                std::cout << "sample format:     " << stream->codecpar->format << std::endl;
                break;
        }

        std::cout << "stream time base: " << stream->time_base.num << " / " << stream->time_base.den << std::endl;
    }
}

}
