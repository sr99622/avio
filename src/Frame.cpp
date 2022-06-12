#include "Frame.h"
#include <sstream>

namespace avio
{

Frame::Frame() :
	m_frame(NULL),
	m_rts(0)
{

}

Frame::Frame(const Frame& other) :
	m_frame(copyFrame(other.m_frame)),
	m_rts(other.m_rts)
{

}

Frame::Frame(Frame&& other) noexcept :
	m_frame(copyFrame(other.m_frame)),
	m_rts(other.m_rts)
{

}

Frame::Frame(AVFrame* src)
{
	av_frame_free(&m_frame);
	m_frame = copyFrame(src);
}

Frame::Frame(int width, int height, AVPixelFormat pix_fmt)
{
	m_rts = AV_NOPTS_VALUE;
	m_frame = av_frame_alloc();
	m_frame->width = width;
	m_frame->height = height;
	m_frame->format = pix_fmt;
	av_frame_get_buffer(m_frame, 0);
	av_frame_make_writable(m_frame);
	int data_size = width * height;

	switch (pix_fmt) {
	case AV_PIX_FMT_YUV420P:
		memset(m_frame->data[0], 0, data_size);
		memset(m_frame->data[1], 128, data_size >> 2);
		memset(m_frame->data[2], 128, data_size >> 2);
		break;
	case AV_PIX_FMT_BGR24:
		memset(m_frame->data[0], 0, data_size * 3);
		break;
	case AV_PIX_FMT_BGRA:
		memset(m_frame->data[0], 0, data_size * 4);
		break;
	default:
		std::cout << "Error: unsupported pix fmt" << std::endl;
	}
}

Frame::Frame(const cv::Mat& mat)
{
	m_rts = 0;
	m_frame = av_frame_alloc();
	AVPixelFormat pix_fmt = AV_PIX_FMT_NONE;
	int width = mat.cols;
	int height = mat.rows;
	int depth = -1;

	switch (mat.type()) {
	case CV_8UC3:
		pix_fmt = AV_PIX_FMT_BGR24;
		depth = 3;
		break;
	case CV_8UC4:
		pix_fmt = AV_PIX_FMT_BGRA;
		depth = 4;
		break;
	default:
		std::cout << "ERROR: unsuspported cv::Mat type" << std::endl;
	}

	m_frame = av_frame_alloc();
	m_frame->width = width;
	m_frame->height = height;
	m_frame->format = pix_fmt;
	av_frame_get_buffer(m_frame, 0);
	av_frame_make_writable(m_frame);
	int linesize = width * depth;

	for (int y = 0; y < height; y++) 
		memcpy(m_frame->data[0] + y * m_frame->linesize[0], mat.data + y * linesize, linesize);
}

Frame::~Frame()
{
	av_frame_free(&m_frame);
	if (mat_buf) delete[] mat_buf;
}

cv::Mat Frame::mat()
{
	cv::Mat mat;
	int cv_format = -1;
	int depth = -1;

	switch (m_frame->format) {
	case AV_PIX_FMT_BGR24:
		cv_format = CV_8UC3;
		depth = 3;
		break;
	case AV_PIX_FMT_BGRA:
		cv_format = CV_8UC4;
		depth = 4;
		break;
	default:
		std::cout << "Error: unsupported pix fmt.  If you intend to convert the frame to cv::Mat format, the incoming frame must be in either bgr24 or bgra pixel format" << std::endl;
		return mat;
	}

	int width = m_frame->width;
	int height = m_frame->height;
	int linesize = width * depth;
	if (mat_buf) delete[] mat_buf;
	mat_buf = new uint8_t[linesize * height];

	for (int y = 0; y < height; y++)
		memcpy(mat_buf + y * linesize, m_frame->data[0] + y * m_frame->linesize[0], linesize);

	mat = cv::Mat(height, width, cv_format, mat_buf, linesize);

	return mat;
}

Frame& Frame::operator=(const Frame& other)
{
	if (other.isValid()) {
		m_rts = other.m_rts;
		av_frame_free(&m_frame);
		m_frame = av_frame_clone(other.m_frame);
		av_frame_make_writable(m_frame);
	}
	else {
		invalidate();
	}
	return *this;
}

Frame& Frame::operator=(Frame&& other) noexcept
{
	if (other.isValid()) {
		m_rts = other.m_rts;
		av_frame_free(&m_frame);
		m_frame = other.m_frame;
		av_frame_make_writable(m_frame);
		other.m_frame = NULL;
	}
	else {
		invalidate();
	}
	return *this;
}

void Frame::invalidate()
{
	av_frame_free(&m_frame);
	m_frame = NULL;
	m_rts = 0;
}

AVFrame* Frame::copyFrame(AVFrame* src)
{
	if (!src)
		return NULL;

	AVFrame* dst = av_frame_alloc();
	dst->format = src->format;
	dst->channel_layout = src->channel_layout;
	dst->sample_rate = src->sample_rate;
	dst->nb_samples = src->nb_samples;
	dst->width = src->width;
	dst->height = src->height;
	av_frame_get_buffer(dst, 0);
	av_frame_make_writable(dst);
	av_frame_copy_props(dst, src);
	av_frame_copy(dst, src);

	return dst;
}

AVMediaType Frame::mediaType() const
{
	AVMediaType result = AVMEDIA_TYPE_UNKNOWN;
	if (isValid()) {
		if (m_frame->width > 0 && m_frame->height > 0)
			result = AVMEDIA_TYPE_VIDEO;
		else if (m_frame->nb_samples > 0 && m_frame->channels > 0)
			result = AVMEDIA_TYPE_AUDIO;
	}
	return result;
}

std::string Frame::description() const
{
	std::stringstream str;
	if (isValid()) {
		if (mediaType() == AVMEDIA_TYPE_VIDEO) {
			const char* pix_fmt_name = av_get_pix_fmt_name((AVPixelFormat)m_frame->format);
			str << "VIDEO FRAME, width: " << m_frame->width << " height: " << m_frame->height
				<< " format: " << (pix_fmt_name ? pix_fmt_name : "unknown pixel format")
				<< " pts: " << m_frame->pts << " m_rts: " << m_rts;
		}
		else if (mediaType() == AVMEDIA_TYPE_AUDIO) {
			const char* sample_fmt_name = av_get_sample_fmt_name((AVSampleFormat)m_frame->format);
			char buf[256];
			av_get_channel_layout_string(buf, 256, m_frame->channels, m_frame->channel_layout);
			str << "AUDIO FRAME, nb_samples: " << m_frame->nb_samples << ", channels: " << m_frame->channels
				<< ", format: " << (sample_fmt_name ? sample_fmt_name : "unknown sample format")
				<< ", sample_rate: " << m_frame->sample_rate
				<< ", channel_layout: " << buf 
				<< ", pts: " << m_frame->pts << ", m_rts: " << m_rts;
		}
		else {
			str << "UNKNOWN MEDIA TYPE";
		}
	}
	else {
		str << "INVALID FRAME";
	}

	return str.str();
}

void Frame::set_rts(AVStream* stream)
{
	if (isValid()) {
		if (m_frame->pts == AV_NOPTS_VALUE) {
			m_rts = 0;
		}
		else {
			double factor = 1000 * av_q2d(stream->time_base);
			uint64_t start_time = (stream->start_time == AV_NOPTS_VALUE ? 0 : stream->start_time);
			m_rts = (pts() - start_time) * factor;
		}
	}
}

void Frame::set_pts(AVStream* stream)
{
	if (isValid()) {
		double factor = av_q2d(stream->time_base);
		m_frame->pts = m_rts / factor / 1000;
	}
}

}
