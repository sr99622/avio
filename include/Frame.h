#pragma once

extern "C" {
#include "libavformat/avformat.h"
#include "libswscale/swscale.h"
#include "libavutil/imgutils.h"
#include "libavutil/pixdesc.h"
#include "libavcodec/avcodec.h"
}

#include "Exception.h"
#include <opencv2/opencv.hpp>

namespace avio
{

class Frame
{
public:
	Frame();
	~Frame();
	Frame(const Frame& other);
	Frame(Frame&& other) noexcept;
	Frame(AVFrame* src);
	Frame(int width, int height, AVPixelFormat pix_fmt);
	Frame(const cv::Mat& mat);
	Frame& operator=(const Frame& other);
	Frame& operator=(Frame&& other) noexcept;
	AVFrame* copyFrame(AVFrame* src);
	bool isValid() const { return m_frame ? true : false; }
	void invalidate();
	AVMediaType mediaType() const;
	uint64_t pts() { return m_frame ? m_frame->pts : AV_NOPTS_VALUE; }
	void set_rts(AVStream* stream);  // called from Decoder::decode
	void set_pts(AVStream* stream);  // called from Encoder::encode
	std::string description() const;
	cv::Mat mat();

	AVFrame* m_frame = NULL;
	uint64_t m_rts;
	bool show = false;
	uint8_t* mat_buf = nullptr;

	ExceptionHandler ex;

};

}

