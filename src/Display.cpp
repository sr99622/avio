#include "Display.h"
#include "PyRunner.h"
#include <filesystem>

namespace avio 
{

void Display::init()
{
    try {
        osd.reader = reader;
        osd.writer = writer;
        osd.display = this;
        
        if (!writer) {
            osd.btnRec->visible = false;
        }
        else {
            if (writer->enabled)
                osd.btnRec->hot = true;
        }

        if (font_file.empty()) {
            CPyObject mod = PyImport_ImportModule("avio");
            std::filesystem::path path(PyModule_GetFilename(mod));
            std::filesystem::path dir = path.parent_path();
            dir.append(PyModule_GetName(mod)).append("Roboto-Regular.ttf");
            font_file = dir.string();
        }

        if (audioFilter) {
            std::cout << "configure filter" << std::endl;
            initAudio(audioFilter->sample_rate(), audioFilter->sample_format(), audioFilter->channels(), audioFilter->channel_layout(), audioFilter->frame_size());
        }
        else if (audioDecoder) {
            std::cout << "configure decoder" << std::endl;
            initAudio(audioDecoder->sample_rate(), audioDecoder->sample_format(), audioDecoder->channels(), audioDecoder->channel_layout(), audioDecoder->frame_size());
        }
    }
    catch (const Exception& e) {
        ex.msg(e.what(), MsgPriority::CRITICAL, "Display constructor exception: ");
    }
}

Display::~Display()
{
    if (SDL_WasInit(SDL_INIT_AUDIO)) SDL_PauseAudioDevice(audioDeviceID, true);
    if (swr_buffer) delete[] swr_buffer;
    if (texture)  SDL_DestroyTexture(texture);
    if (renderer) SDL_DestroyRenderer(renderer);
    if (window)   SDL_DestroyWindow(window);
    TTF_Quit();
    SDL_Quit();
}

int Display::initVideo(int width, int height, AVPixelFormat pix_fmt)
{
    int ret = 0;
    try {
        Uint32 sdl_format = 0;
        int w = width;
        int h = height;

        switch (pix_fmt) {
        case AV_PIX_FMT_YUV420P:
        case AV_PIX_FMT_YUVJ420P:
            sdl_format = SDL_PIXELFORMAT_IYUV;
            break;
        case AV_PIX_FMT_RGB24:
            sdl_format = SDL_PIXELFORMAT_RGB24;
            break;
        case AV_PIX_FMT_RGBA:
            sdl_format = SDL_PIXELFORMAT_RGBA32;
            break;
        case AV_PIX_FMT_BGR24:
            sdl_format = SDL_PIXELFORMAT_BGR24;
            break;
        case AV_PIX_FMT_BGRA:
            sdl_format = SDL_PIXELFORMAT_BGRA32;
            break;
        default:
            const char* pix_fmt_name = av_get_pix_fmt_name(pix_fmt);
            std::stringstream str;
            str << "unsupported pix fmt: " << (pix_fmt_name ? pix_fmt_name : std::to_string(pix_fmt));
            throw Exception(str.str());
        }

        osd.format = sdl_format;

        if (!SDL_WasInit(SDL_INIT_VIDEO))
            if (SDL_Init(SDL_INIT_VIDEO)) throw Exception(std::string("SDL video init error: ") + SDL_GetError());

        if (!window) {
            const char* pix_fmt_name = av_get_pix_fmt_name(pix_fmt);
            std::stringstream str;
            str << "initializing video display | width: " << width << " height: " << height
                << " pixel format: " << pix_fmt_name ? pix_fmt_name : "unknown pixel format";
            ex.msg(str.str());

            window = SDL_CreateWindow("window", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, w, h, 0);
            if (!window) throw Exception(std::string("SDL_CreateWindow") + SDL_GetError());

            renderer = SDL_CreateRenderer(window, -1, 0);
            if (!renderer) throw Exception(std::string("SDL_CreateRenderer") + SDL_GetError());

            texture = SDL_CreateTexture(renderer, sdl_format, SDL_TEXTUREACCESS_STREAMING, w, h);
            if (!texture) throw Exception(std::string("SDL_CreateTexture") + SDL_GetError());

            ex.ck(TTF_Init(), "TTF_Init");

            int font_size = 24;
            if (width < 960) font_size = 16;
            osd.font = TTF_OpenFont(font_file.c_str(), font_size);
            if (!osd.font) {
                std::stringstream str;
                str << "Attempted to find font file at " << font_file << "\n";
                str << "ERROR: Font file for osd not found, osd has been disabled.\n";
                str << "       This error may be fixed by placing the font file at the location above\n"; 
                str << "       or the font file location may be set manually using the font_file parameter\n";
                std::cout << str.str() << std::endl;
                osd_enabled = false;
            }
        }
        else {
            int window_width;
            int window_height;
            SDL_GetWindowSize(window, &window_width, &window_height);
            if (!(window_width == w && window_height == h)) {
                SDL_SetWindowSize(window, w, h);
                SDL_DisplayMode DM;
                SDL_GetCurrentDisplayMode(0, &DM);
                auto Width = DM.w;
                auto Height = DM.h;
                int x = (Width - w) / 2;
                int y = (Height - h) / 2;
                SDL_SetWindowPosition(window, x, y);
                if (texture)
                    SDL_DestroyTexture(texture);
                texture = SDL_CreateTexture(renderer, sdl_format, SDL_TEXTUREACCESS_STREAMING, w, h);
            }
        }
    }
    catch (const Exception& e) {
        ex.msg(e.what(), MsgPriority::CRITICAL, "Display::initVideo exception: ");
        ret = -1;
    }
    
    return ret;
}

void Display::videoPresentation()
{
    if (f.m_frame->format == AV_PIX_FMT_YUV420P) {
        ex.ck(SDL_UpdateYUVTexture(texture, NULL,
            f.m_frame->data[0], f.m_frame->linesize[0],
            f.m_frame->data[1], f.m_frame->linesize[1],
            f.m_frame->data[2], f.m_frame->linesize[2]), 
            SDL_GetError());
    }
    else {
        ex.ck(SDL_UpdateTexture(texture, NULL, f.m_frame->data[0], f.m_frame->linesize[0]), SDL_GetError());
    }

    SDL_RenderClear(renderer);
    ex.ck(SDL_RenderCopy(renderer, texture, NULL, NULL), SDL_GetError());
    osd.render(renderer);
    SDL_RenderPresent(renderer);
}

void Display::clearInputQueues()
{
	if (vfq_in) while (vfq_in->size() > 0) vfq_in->pop();
	if (afq_in) while (afq_in->size() > 0) afq_in->pop();
}

PlayState Display::getEvents(std::vector<SDL_Event>* events)
{
    PlayState state = PlayState::PLAY;
    SDL_Event event;
    while (SDL_PollEvent(&event))
        events->push_back(event);

    if (events->empty()) {
        SDL_Event user_event = { 0 };
        user_event.type = SDL_USEREVENT;
        events->push_back(user_event);
    }

    for (int i = 0; i < events->size(); i++) {
        SDL_Event event = events->at(i);
        if (event.type == SDL_QUIT) 
            state = PlayState::QUIT;
        else if (event.type == SDL_KEYDOWN) {
            if (event.key.keysym.sym == SDLK_ESCAPE) {
                state = PlayState::QUIT;
            }
            else if (event.key.keysym.sym == SDLK_SPACE) {
                state = PlayState::PAUSE;
            }
            else if (event.key.keysym.sym == SDLK_LEFT && event.key.repeat == 0) {
                if (vfq_in) {
                    reader->seek_target_pts = reader->last_video_pts - av_q2d(av_inv_q(reader->video_time_base()));
                }
                else {
                    float pct = (f.m_rts - reader->start_time()) / (float)reader->duration();
                    if (pct > 0.02)
                        pct -= 0.01;
                    else
                        pct = 0.0;
                    reader->request_seek(pct);
                }
                clearInputQueues();
            }
            else if (event.key.keysym.sym == SDLK_RIGHT && event.key.repeat == 0) {
                if (vfq_in) {
                    reader->seek_target_pts = reader->last_video_pts + av_q2d(av_inv_q(reader->video_time_base()));
                }
                else {
                    float pct = (f.m_rts - reader->start_time()) / (float)reader->duration();
                    if (pct < 0.98) {
                        pct += 0.01;
                        reader->request_seek(pct);
                    }
                }
                clearInputQueues();
            }
            else if (event.key.keysym.sym == SDLK_s) {
                if (paused) single_step = true;
            }
            else if (event.key.keysym.sym == SDLK_a) {
                if (paused) reverse_step = true;
            }
            else if (event.key.keysym.sym == SDLK_r) {
                key_record_flag = true;
            }
        }
    }
    return state;
}

bool Display::display()
{
    bool playing = true;

    while (true)
    {
        std::vector<SDL_Event> events;
        PlayState state = getEvents(&events);

        if (state == PlayState::QUIT) {
            audio_eof = true;
            playing = false;
            break;
        }
        else if (state == PlayState::PAUSE) {
            togglePause();
            break;
        }

        if (paused) 
        {
            if (!single_step && !reverse_step) {
                if (reader->seeking()) {
                    paused = false;
                }
                else {
                    f = paused_frame;
                    if (havePython()) pyRunner->run(f, Event::pack(events));
                    if (osd_enabled) for (SDL_Event& event : events) osd.handleEvent(event, f);
                    videoPresentation();
                    SDL_Delay(SDL_EVENT_LOOP_WAIT);
                    break;
                }
            }
        }

        try 
        {
            if (!vfq_in) {
                SDL_Delay(SDL_EVENT_LOOP_WAIT);
                f = Frame(640, 480, AV_PIX_FMT_YUV420P);
                f.m_rts = rtClock.stream_time();
            }
            else {
                if (reverse_step) {
                    if (recent.empty() || recent_idx < 0) {
                        std::cout << "recent frame queue empty" << std::endl;
                        reverse_step = false;
                        break;
                    }
                    else {
                        if (recent[recent_idx].m_frame->pts == f.m_frame->pts && recent_idx > 0) recent_idx--;
                        f = recent[recent_idx];
                        recent_idx--;
                    }
                }
                else {
                    if (recent_idx < (int)(recent.size() - 1) && !recent.empty()) {
                        recent_idx++;
                        if (recent[recent_idx].m_frame->pts == f.m_frame->pts && recent_idx < (int)(recent.size() - 1)) recent_idx++;
                        f = recent[recent_idx];
                    }
                    else {
                        if (request_recent_clear) {
                            recent.clear();
                            request_recent_clear = false;
                        }
                        vfq_in->pop(f);
                        recent.push_back(f);
                        if (recent.size() > recent_q_size)
                            recent.pop_front();
                        recent_idx = recent.size() - 1;
                    }
                }
            }

            if (reader->seeking()) {
                if (f.m_frame->pts != reader->seek_found_pts) {
                    paused = false;
                    request_recent_clear = true;
                }
                else {
                    reader->seek_found_pts = AV_NOPTS_VALUE;
                    paused = user_paused;
                }
            }

            paused_frame = f;

            if (Py_IsInitialized() && havePython()) {
                //if (fix_audio_pop) SDL_LockAudioDevice(audioDeviceID);
                if (!pyRunner)
                    pyRunner = new PyRunner(pythonDir, pythonFile, pythonClass, pythonInitArg);

                if (f.isValid()) {
                    if (pyRunner->run(f, Event::pack(events)))
                        toggleRecord();
                }
                //if (fix_audio_pop) SDL_UnlockAudioDevice(audioDeviceID);
            }

            if (f.isValid()) {
                ex.ck(initVideo(f.m_frame->width, f.m_frame->height, (AVPixelFormat)f.m_frame->format), "initVideo");
                if (osd_enabled) for (SDL_Event& event : events) osd.handleEvent(event, f);
                if (key_record_flag) {
                    key_record_flag = false;
                    toggleRecord();
                }

                if ((!afq_in || reader->vpq_max_size > 1) && !ignore_video_pts)
                    SDL_Delay(rtClock.update(f.m_rts - reader->start_time()));
                
                if (!reader->seeking()) videoPresentation();
                reader->last_video_pts = f.m_frame->pts;

                if (single_step || reverse_step) {
                    single_step = false;
                    reverse_step = false;
                }

                if (vfq_out)
                    vfq_out->push(f);

            }
            else {
                ex.msg("Display receive null eof");
                playing = false;
                break;
            }
        }
        catch (const QueueClosedException& e) {
            playing = false;
            ex.msg(e.what(), MsgPriority::INFO, "Display::display exception: ");
            break;
        }
        catch (const Exception& e) {
            ex.msg(e.what(), MsgPriority::CRITICAL, "Display::display exception: ");
            ex.msg(std::string("last frame description: ") + f.description());
            playing = false;
            break;
        }
    }

    return playing;
}

int Display::initAudio(int stream_sample_rate, AVSampleFormat stream_sample_format, int stream_channels, uint64_t stream_channel_layout, int stream_nb_samples)
{
    int ret = 0;
    try {

        if (stream_nb_samples == 0) {
            int audio_frame_size = av_samples_get_buffer_size(NULL, stream_channels, 1, sdl_sample_format, 1);
            int bytes_per_second = av_samples_get_buffer_size(NULL, stream_channels, stream_sample_rate, sdl_sample_format, 1);
            stream_nb_samples = bytes_per_second * 0.02f / audio_frame_size;
            std::cout << "bytes_per_second: " << bytes_per_second << " stream_nb_samples: " << stream_nb_samples << std::endl;
        }

        sdl.channels = stream_channels;
        sdl.freq = stream_sample_rate;
        sdl.silence = 0;
        sdl.samples = stream_nb_samples;
        sdl.userdata = this;
        sdl.callback = AudioCallback;

        switch (sdl_sample_format) {
        case AV_SAMPLE_FMT_FLT:
            sdl.format = AUDIO_F32;
            break;
        case AV_SAMPLE_FMT_S16:
            sdl.format = AUDIO_S16;
            break;
        case AV_SAMPLE_FMT_U8:
            sdl.format = AUDIO_U8;
            break;
        default:
            const char* result = "unkown sample format";
            const char* name = av_get_sample_fmt_name(sdl_sample_format);
            if (name)
                result = name;
            std::cout << "ERROR: incompatible sample format: " << result << std::endl;
            std::cout << "supported formats: AV_SAMPLE_FMT_FLT, AV_SAMPLE_FMT_S16, AV_SAMPLE_FMT_U8" << std::endl;
            std::exit(0);
        }

        audio_buffer_len = av_samples_get_buffer_size(NULL, sdl.channels, sdl.samples, sdl_sample_format, 1);
        sdl_buffer.set_max_size(audio_buffer_len * 10);

        ex.ck(swr_ctx = swr_alloc_set_opts(NULL, stream_channel_layout, sdl_sample_format, stream_sample_rate,
            stream_channel_layout, stream_sample_format, stream_sample_rate, 0, NULL), SASO);
        ex.ck(swr_init(swr_ctx), SI);

        int num_drivers = SDL_GetNumAudioDrivers();
        for (int i = 0; i < num_drivers; i++)
            std::cout << "audio driver: " << i << " : " << SDL_GetAudioDriver(i) << std::endl;

        int num_devices = SDL_GetNumAudioDevices(0);
        for (int i = 0; i < num_devices; i++)
            std::cout << "audio device: " << i << " : " << SDL_GetAudioDeviceName(i, 0) << std::endl;

        if (!SDL_WasInit(SDL_INIT_AUDIO)) {
            if (SDL_Init(SDL_INIT_AUDIO))
                throw Exception(std::string("SDL audio init error: ") + SDL_GetError());
        }

        audioDeviceID = SDL_OpenAudioDevice(NULL, 0, &sdl, &have, 0);
        if (audioDeviceID == 0) {
            throw Exception(std::string("SDL_OpenAudioDevice exception: ") + SDL_GetError());
        }

        SDL_PauseAudioDevice(audioDeviceID, 0);

    }
    catch (const Exception& e) {
        ex.msg(e.what(), MsgPriority::CRITICAL, "Display::initAudio exception: ");
        std::exit(0);
    }

    return ret;
}

void Display::AudioCallback(void* userdata, uint8_t* audio_buffer, int len)
{
    Display* d = (Display*)userdata;
    memset(audio_buffer, 0, len);
    Frame f;

    if (d->paused)
        return;

    try {
        if (d->disable_audio || d->user_paused)
            return;

        while (len > 0) {
            if (d->sdl_buffer.size() < d->audio_buffer_len) {
                d->afq_in->pop(f);
                if (d->afq_out) d->afq_out->push(f);

                if (f.isValid()) {
                    uint64_t channels = f.m_frame->channels;
                    int nb_samples = f.m_frame->nb_samples;
                    const uint8_t** data = (const uint8_t**)&f.m_frame->data[0];
                    int frame_buffer_size = av_samples_get_buffer_size(NULL, channels, nb_samples, d->sdl_sample_format, 0);
                        
                    if (frame_buffer_size != d->swr_buffer_size) {
                        if (d->swr_buffer) delete[] d->swr_buffer;
                        d->swr_buffer = new uint8_t[frame_buffer_size];
                        d->swr_buffer_size = frame_buffer_size;
                    }

                    swr_convert(d->swr_ctx, &d->swr_buffer, nb_samples, data, nb_samples);
                    for (int i = 0; i < d->swr_buffer_size; i++)
                        d->sdl_buffer.push(d->swr_buffer[i]);
                }
                else {
                    SDL_PauseAudioDevice(d->audioDeviceID, true);
                    len = -1;
                    d->ex.msg("audio callback received eof");
                    d->audio_eof = true;
                    if (!d->vfq_in) {
                        SDL_Event event;
                        event.type = SDL_QUIT;
                        SDL_PushEvent(&event);
                        return;
                    }
                }
            }

            while (d->sdl_buffer.size() > 0 && len > 0) {
                audio_buffer[d->audio_buffer_len - len] = d->sdl_buffer.pop();
                len--;
            }

            d->rtClock.sync(f.m_rts); 
            d->reader->seek_found_pts = AV_NOPTS_VALUE;

        }
    }
    catch (const QueueClosedException& e) { }
}

bool Display::isPaused()
{
    return paused;
}

void Display::togglePause()
{
    paused = !paused;
    rtClock.pause(paused);
    user_paused = paused;
    osd.btnPlay->hot = paused;
    //if (SDL_WasInit(SDL_INIT_AUDIO) && fix_audio_pop) SDL_PauseAudioDevice(audioDeviceID, paused);
}

void Display::toggleRecord()
{
    if (!writer) {
        std::cout << "Error: no writer specified" << std::endl;
        return;
    }

    recording = !recording;

    if (prepend_recent_write && recording) {
        for (int i = 0; i < recent.size() - 1; i++)
            vfq_out->push(recent[i]);
    }

    writer->enabled = recording;
    osd.btnRec->hot = recording;
}

bool Display::havePython()
{
    if (pythonDir.empty() || pythonFile.empty() || pythonClass.empty())
        return false;
    else
        return true;
}

void Display::pin_osd(bool arg)
{
    osd.pin_osd = arg;
}

std::string Display::audioDeviceStatus() const
{
    std::stringstream str;
    bool output = false;
    int count = SDL_GetNumAudioDevices(output);
    for (int i = 0; i < count; i++)
        str << "audio device: " << i << " name: " << SDL_GetAudioDeviceName(i, output) << "\n";

    str << "selected audio device ID (+2): " << audioDeviceID << "\n";
    str << "CHANNELS  want: " << (int)sdl.channels << "\n          have: " << (int)have.channels << "\n";
    str << "FREQUENCY want: " << sdl.freq << "\n          have: " << have.freq << "\n";
    str << "SAMPLES   want: " << sdl.samples << "\n          have: " << have.samples << "\n";
    str << "FORMAT    want: " << sdlAudioFormatName(sdl.format) << "\n          have: " << sdlAudioFormatName(have.format) << "\n";
    str << "SIZE      want: " << sdl.size << "\n          have: " << have.size << "\n";
    return str.str();
}

const char* Display::sdlAudioFormatName(SDL_AudioFormat format) const 
{
    /*
     Note: SDL does not support planar format audio

     AV_SAMPLE_FMT_NONE = -1,
     AV_SAMPLE_FMT_U8,          ///< unsigned 8 bits
     AV_SAMPLE_FMT_S16,         ///< signed 16 bits
     AV_SAMPLE_FMT_S32,         ///< signed 32 bits
     AV_SAMPLE_FMT_FLT,         ///< float
     AV_SAMPLE_FMT_DBL,         ///< double
    */

    switch (format) {
    case AUDIO_S8:
        return "AUDIO_S8";
        break;
    case AUDIO_U8:
        return "AUDIO_U8";
        break;
    case AUDIO_S16:
        return "AUDIO_S16";
        break;
    case AUDIO_U16:
        return "AUDIO_U16";
        break;
    case AUDIO_S32:
        return "AUDIO_S32";
        break;
    case AUDIO_F32:
        return "AUDIO_F32";
        break;
    default:
        return "UNKNOWN";
    }
}

}
