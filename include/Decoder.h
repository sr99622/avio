#pragma once

#include "Exception.h"
#include "Queue.h"
#include "Frame.h"
#include "Reader.h"

namespace avio
{

class Decoder
{
public:
	Decoder(Reader& reader, AVMediaType mediaType, AVHWDeviceType hw_device_type = AV_HWDEVICE_TYPE_NONE);

	~Decoder();
	int decode(AVPacket* pkt);
	void close();

	int sample_rate() { return dec_ctx->sample_rate; }
	int channels() { return dec_ctx->channels; }
	int frame_size() { return reader->fmt_ctx->streams[stream_index]->codecpar->frame_size; }
	uint64_t channel_layout() { return dec_ctx->channel_layout; }
	AVSampleFormat sample_format() { return dec_ctx->sample_fmt; }
	int bit_rate() { return dec_ctx->bit_rate; }
	int width() { return dec_ctx->width; }
	int height() { return dec_ctx->height; }
	AVPixelFormat pix_fmt() { return dec_ctx->pix_fmt; }
	int64_t nb_frames() { return reader->fmt_ctx->streams[stream_index]->nb_frames; }
	int64_t duration() { return reader->fmt_ctx->streams[stream_index]->duration; }
	AVRational time_base() { return reader->fmt_ctx->streams[stream_index]->time_base; }

	AVMediaType mediaType;
	std::string strMediaType;
	AVFrame* frame = NULL;
	AVFrame* sw_frame = NULL;
	AVFrame* cvt_frame = NULL;
	AVStream* stream = NULL;
	const AVCodec* dec = NULL;
	AVCodecContext* dec_ctx = NULL;
	AVBufferRef* hw_device_ctx = NULL;
	SwsContext* sws_ctx = NULL;

	int stream_index;
	Reader* reader;

	bool show_frames = false;

	Queue<Frame>* frame_q = nullptr;
	Queue<AVPacket*>* pkt_q = nullptr;

	std::string frame_q_name;
	std::string pkt_q_name;

	std::string video_in() const { return std::string(pkt_q_name); }
	std::string audio_in() const { return std::string(pkt_q_name); }
	std::string video_out() const { return std::string(frame_q_name); }
	std::string audio_out() const { return std::string(frame_q_name); }
	void set_video_in(const std::string& name) { pkt_q_name = std::string(name); }
	void set_audio_in(const std::string& name) { pkt_q_name = std::string(name); }
	void set_video_out(const std::string& name) { frame_q_name = std::string(name); }
	void set_audio_out(const std::string& name) { frame_q_name = std::string(name); }

	ExceptionHandler ex;
};

}
