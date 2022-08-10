#pragma once

#define SDL_MAIN_HANDLED

#include <SDL.h>
#include <chrono>
#include <deque>
#include "SDL_ttf.h"
#include "Exception.h"
#include "Queue.h"
#include "Frame.h"
#include "Clock.h"
#include "Decoder.h"
#include "Filter.h"
#include "PyRunner.h"
#include "Osd.h"
#include "Reader.h"
#include "Writer.h"
#include "Encoder.h"
#include "Event.h"

#define SDL_EVENT_LOOP_WAIT 10

namespace avio
{

enum class PlayState {
    PLAY,
    PAUSE,
    QUIT
};

class Display
{
public:
    Display(Reader& reader) : reader(&reader) {  }
    ~Display();

    void init();
    int initAudio(int sample_rate, AVSampleFormat sample_fmt, int channels, uint64_t channel_layout, int stream_nb_sampples);
    int initVideo(int width, int height, AVPixelFormat pix_fmt);
    static void AudioCallback(void* userdata, uint8_t* stream, int len);
    void videoPresentation();
    PlayState getEvents(std::vector<SDL_Event>* events);
    bool display();
    bool havePython();
    void pin_osd(bool arg);
    void enable_status(bool arg);
    void clearInputQueues();
    
    bool paused = false;
    bool user_paused = false;
    Frame paused_frame;
    bool isPaused();
    void togglePause();
    bool single_step = false;
    bool reverse_step = false;
    int recent_idx = -1;

    bool key_record_flag = false;
    bool recording = false;
    void toggleRecord();

    Frame f;

    std::string audioDeviceStatus() const;
    const char* sdlAudioFormatName(SDL_AudioFormat format) const;

    SDL_Window* window = NULL;
    SDL_Renderer* renderer = NULL;
    SDL_Texture* texture = NULL;
    SDL_Surface* screen = NULL;
    SDL_AudioSpec sdl = { 0 };
    SDL_AudioSpec have = { 0 };

    std::string pythonDir;
    std::string pythonFile;
    std::string pythonClass;
    std::string pythonInitArg;

    std::string vfq_in_name;
    std::string afq_in_name;
    std::string vfq_out_name;
    std::string afq_out_name;

    Queue<Frame>* vfq_in = nullptr;
    Queue<Frame>* afq_in = nullptr;
    Queue<Frame>* vfq_out = nullptr;
    Queue<Frame>* afq_out = nullptr;

    std::string video_in() const { return std::string(vfq_in_name); }
    std::string audio_in() const { return std::string(afq_in_name); }
    std::string video_out() const { return std::string(vfq_out_name); }
    std::string audio_out() const { return std::string(afq_out_name); }
    void set_video_in(const std::string& name) { vfq_in_name = std::string(name); }
    void set_audio_in(const std::string& name) { afq_in_name = std::string(name); }
    void set_video_out(const std::string& name) { vfq_out_name = std::string(name); }
    void set_audio_out(const std::string& name) { afq_out_name = std::string(name); }

    PyRunner* pyRunner = nullptr;

    Osd osd;
    std::string font_file;
    bool osd_enabled = true;

    bool fullscreen = false;

    SDL_AudioDeviceID audioDeviceID;
    Clock rtClock;

    SwrContext* swr_ctx;
    AVSampleFormat sdl_sample_format = AV_SAMPLE_FMT_S16;

    uint8_t* swr_buffer = nullptr;
    int swr_buffer_size = 0;
    Queue<char> sdl_buffer;
    int audio_buffer_len = 0;
    bool disable_audio = false;
    bool ignore_video_pts = false;
    bool audio_eof = false;

    int width = 0;
    int height = 0;
    AVPixelFormat pix_fmt = AV_PIX_FMT_NONE;

    uint64_t start_time;
    uint64_t duration;

    std::chrono::steady_clock clock;

    std::deque<Frame> recent;
    bool request_recent_clear = false;
    int recent_q_size = 200;
    bool prepend_recent_write = false;

    Reader* reader = nullptr;
    Writer* writer = nullptr;
    Decoder* audioDecoder = nullptr;
    Filter* audioFilter = nullptr;

    ExceptionHandler ex;
};

}


