#include "Exception.h"
#include "Queue.h"
#include "Reader.h"
#include "Decoder.h"
#include "Encoder.h"
#include "Writer.h"
#include "Pipe.h"
#include "Filter.h"
#include "Display.h"

namespace avio
{

static void show_pkt(AVPacket* pkt)
{
    std::stringstream str;
    str 
        << " index: " << pkt->stream_index
        << " flags: " << pkt->flags
        << " pts: " << pkt->pts
        << " dts: " << pkt->dts
        << " size: " << pkt->size
        << " duration: " << pkt->duration;

    std::cout << str.str() << std::endl;
}

static void read(Reader* reader, Queue<AVPacket*>* vpq, Queue<AVPacket*>* apq) 
{
    if (reader->vpq_max_size > 0) vpq->set_max_size(reader->vpq_max_size);
    if (reader->apq_max_size > 0) apq->set_max_size(reader->apq_max_size);

    try {
        while (AVPacket* pkt = reader->read())
        {
            if (reader->seek_target_pts != AV_NOPTS_VALUE) {
                av_packet_free(&pkt);
                pkt = reader->seek();
                if (!pkt) {
                    break;
                }
                if (vpq) while(vpq->size() > 0) vpq->pop();
                if (apq) while(apq->size() > 0) apq->pop();
            }

            if (reader->stop_play_at_pts != AV_NOPTS_VALUE && pkt->stream_index == reader->seek_stream_index()) {
                if (pkt->pts > reader->stop_play_at_pts) {
                    av_packet_free(&pkt);
                    break;
                }
            }

            if (pkt->stream_index == reader->video_stream_index) {
                if (reader->show_video_pkts) show_pkt(pkt);
                if (vpq)
                    vpq->push(pkt);
                else
                    av_packet_free(&pkt);
            }

            else if (pkt->stream_index == reader->audio_stream_index) {
                if (reader->show_audio_pkts) show_pkt(pkt);
                if (apq)
                    apq->push(pkt);
                else
                    av_packet_free(&pkt);
            }
        }
        if (vpq) vpq->push(NULL);
        if (apq) apq->push(NULL);
    }
    catch (const QueueClosedException& e) {}
    catch (const Exception& e) { std::cout << " reader failed: " << e.what() << std::endl; }
}

static void decode(Decoder* decoder, Queue<AVPacket*>* pkt_q, Queue<Frame>* frame_q) 
{
    decoder->frame_q = frame_q;
    decoder->pkt_q = pkt_q;

    try {
        while (AVPacket* pkt = pkt_q->pop())
        {
            decoder->decode(pkt);
            av_packet_free(&pkt);
        }

        std::cout << decoder->strMediaType << " decoder rcvd null pkt eof " << std::endl;

        decoder->decode(NULL);
        decoder->frame_q->push(Frame(nullptr));
    }
    catch (const QueueClosedException& e) { }
    catch (const Exception& e) { std::cout << decoder->strMediaType << " decoder failed: " << e.what() << std::endl; }
}

static void filter(Filter* filter, Queue<Frame>* q_in, Queue<Frame>* q_out)
{
    try {
        Frame f;
        filter->frame_out_q = q_out;
        while (true)
        {
            q_in->pop(f);
            filter->filter(f);
            if (!f.isValid())
                break;
        }
        filter->frame_out_q->push(Frame(nullptr));
    }
    catch (const QueueClosedException& e) {}
}

static void write(Writer* writer, Encoder* encoder)
{
    try {

        Frame f;
        while (true) 
        {
            encoder->frame_q->pop(f);
            if (encoder->show_frames) std::cout << f.description() << std::endl;
            if (writer->enabled) {

                if (!encoder->opened)
                    encoder->init();

                if (!writer->opened) {
                    std::string filename;
                    if (!writer->write_dir.empty())
                        filename = writer->write_dir + "/";

                    if (writer->filename.empty()) {
                        std::time_t t = std::time(nullptr);
                        std::tm tm = *std::localtime(&t);
                        std::stringstream str;
                        str << std::put_time(&tm, "%y%m%d%H%M%S");
                        filename += str.str() + "." + writer->m_format;
                    }
                    else {
                        filename += writer->filename;
                    }
                    writer->open(filename);
                }

                if (writer->opened && encoder->opened) encoder->encode(f);
            }
            else {

                if (writer->opened) {
                    if (encoder->opened) {
                        Frame tmp(nullptr);
                        encoder->encode(tmp);
                        encoder->close();
                    }
                    writer->close();
                }
            }
        }
    }
    catch (const QueueClosedException& e) 
    { 
        if (writer->opened) {
            if (encoder->opened) {
                Frame tmp(nullptr);
                encoder->encode(tmp);
                encoder->close();
            }
            writer->close();
        }
    }
}

static void pkt_drain(Queue<AVPacket*>* pkt_q) 
{
    try {
        while (AVPacket* pkt = pkt_q->pop())
        {
            av_packet_free(&pkt);
        }
    }
    catch (const QueueClosedException& e) {}
}

static void frame_drain(Queue<Frame>* frame_q) 
{
    Frame f;
    try {
        while (true) 
        {
            frame_q->pop(f);
            if (!f.isValid())
                break;
        }
    }
    catch (const QueueClosedException& e) {}
}

}
