#pragma once

#define SDL_MAIN_HANDLED

#include <SDL.h>
#include <chrono>
#include "SDL_ttf.h"
#include "Exception.h"
#include "Queue.h"
#include "Frame.h"
#include "Clock.h"
#include "Decoder.h"
#include "PyRunner.h"
#include "Hud.h"
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
    int initAudio(int sample_rate, AVSampleFormat sample_fmt, int channels, uint64_t channel_layout);
    int initVideo(int width, int height, AVPixelFormat pix_fmt);
    static void AudioCallback(void* userdata, uint8_t* stream, int len);
    void videoPresentation();
    PlayState getEvents(std::vector<SDL_Event>* events);
    bool display();
    bool havePython();
    void pin_hud(bool arg);

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
    SDL_AudioSpec want = { 0 };
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

    Hud hud;
    std::string font_file;
    bool hud_enabled = true;

    SwrContext* swr_ctx;
    SDL_AudioDeviceID audioDeviceID;
    Clock rtClock;

    int sample_rate = 0;
    int channels = 0;
    int nb_samples = 0;
    int64_t channel_layout = 0;
    AVSampleFormat sample_format = AV_SAMPLE_FMT_NONE;
    AVSampleFormat audio_playback_format = AV_SAMPLE_FMT_NONE;

    int width = 0;
    int height = 0;
    AVPixelFormat pix_fmt = AV_PIX_FMT_NONE;

    uint8_t* audioBuf = nullptr;
    int dataSize = 0;
    bool disable_audio = false;
    bool fix_audio_pop = false;
    bool ignore_video_pts = false;
    bool audio_eof = false;

    uint64_t start_time;
    uint64_t duration;

    std::deque<Frame> recent;
    bool request_recent_clear = false;
    int recent_q_size = 200;
    bool prepend_recent_write = false;

    Reader* reader = nullptr;
    Writer* writer = nullptr;

    ExceptionHandler ex;
};

}


