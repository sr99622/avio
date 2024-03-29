#include "Osd.h"
#include "Display.h"
#include <ctime>

namespace avio
{

Osd::Osd()
{
    timeout_start = time(nullptr);
    bar = new ProgressBar(this);
    widgets.push_back(bar);
    lblTime = new Label(this);
    widgets.push_back(lblTime);
    lblMark = new Label(this);
    widgets.push_back(lblMark);
    btnRec = new ButtonRec(this);
    widgets.push_back(btnRec);
    btnPlay = new ButtonPlay(this);
    widgets.push_back(btnPlay);
    btnJpeg = new ButtonJpeg(this);
    widgets.push_back(btnJpeg);

    build_status();
}

std::string Osd::strElapsed(int64_t elapsed) const
{
    int seconds = (int)(elapsed / (float)1000) % 60;
    int minutes = (int)(elapsed / (float)60000) % 60;
    std::stringstream str;
    str.fill('0');
    str.width(2);
    str << minutes << ":";
    str.fill('0');
    str.width(2);
    str << seconds;
    return str.str();
}

void Osd::showMark(float pct) 
{
    lblMark->visible = true;
    lblMark->font = font;
    std::string mark = strElapsed(reader->duration() * pct);
    SDL_Point text_size = lblMark->setText(mark.c_str());
    lblMark->x = bar->x + pct * bar->width - pct * text_size.x;
    lblMark->y = bar->y - bar->height - text_size.y + 8;
}

void Osd::render(SDL_Renderer* renderer)
{
    if (heads_up || pin_osd) {
        for (Widget* widget : widgets)
            widget->render(renderer);
    }
}

void Osd::fade(Frame& f)
{
    if (f.m_faded) return;

    if (((Display*)display)->recording) return;

    int menu_height = f.m_frame->height * 0.15f;
    int menu_row = 0;
    float gradient = 0.70f / menu_height;

    for (int y = f.m_frame->height - menu_height; y < f.m_frame->height; y++) {
        for (int x = 0; x < f.m_frame->linesize[0]; x++) {
            int i = y * f.m_frame->linesize[0] + x;
            f.m_frame->data[0][i] *= (1 - menu_row * gradient);
        }
        menu_row++;
    }

    if (status_enabled) status_background(f);

    f.m_faded = true;
}

void Osd::build_status()
{
    lblPyRuntime = new Label(this);
    widgets.push_back(lblPyRuntime);
    lblRTS = new Label(this);
    widgets.push_back(lblRTS);
}

void Osd::status_background(Frame& f) 
{
    panel_start_row = 0;

    SDL_Point lblPyRuntime_text_size = lblPyRuntime->setText(lblPyRuntime_text);
    panel_stop_row = 4 + lblPyRuntime_text_size.y;

    panel_stop_column = f.m_frame->linesize[0];

    for (int y = panel_start_row; y < panel_stop_row; y++) {
        for (int x = 0; x < panel_stop_column; x++) {
            int i = y * f.m_frame->linesize[0] + x;
            f.m_frame->data[0][i] *= 0.2;
        }
    }
}

void Osd::handle_status(Frame& f)
{
    lblPyRuntime->font = font;
    SDL_Point lblPyRuntime_text_size = lblPyRuntime->setText(lblPyRuntime_text);
    lblPyRuntime->x = 16;
    lblPyRuntime->y = panel_start_row;

    lblRTS->font = font;
    SDL_Point lblRTS_text_size = lblRTS->setText(lblRTS_text);
    lblRTS->x = 64 + lblPyRuntime_text_size.x;
    lblRTS->y = panel_start_row;
}

void Osd::handleEvent(SDL_Event& e, Frame& f) 
{
    if (!f.isValid())
        return;

    if (time(nullptr) - timeout_start > TIMEOUT)
        heads_up = false;

    if (e.type == SDL_MOUSEMOTION) {

        if (e.motion.x != last_x || e.motion.y != last_y) {
            timeout_start = time(nullptr);
            heads_up = true;
            last_x = e.motion.x;
            last_y = e.motion.y;
        }
    }

    if (heads_up || pin_osd) {

        if (!font) 
            return;

        bar->x = f.m_frame->width * 0.1f;
        bar->width = f.m_frame->width * 0.75f;
        bar->y = f.m_frame->height * 0.95f;
        bar->height = 8;

        if (reader->duration() > 0) {
            bar->pct_progress = (f.m_rts - reader->start_time()) / (float)reader->duration();
        }
        else {
            bar->pct_progress = 0;
            bar->seek_bar_enabled = false;
        }

        lblTime->font = font;
        std::string elapsed = strElapsed(f.m_rts - reader->start_time());
        SDL_Point text_size = lblTime->setText(elapsed.c_str());
        lblTime->x = bar->x - text_size.x - lblTime->border.right - bar->border.left;
        lblTime->y = bar->y - (int) text_size.y / 2.0f + (int) bar->height / 2.0f;

        btnPlay->font = font;
        SDL_Point btnPlay_size = btnPlay->setText("||");
        btnPlay->x = bar->x + bar->width + 16;
        btnPlay->width = btnRec->width * 0.5f;
        btnPlay->y = bar->y - (int)btnPlay_size.y / 2.0f + (int)bar->height / 2.0f;

        btnRec->font = font;
        SDL_Point btnRec_size = btnRec->setText("Rec");
        btnRec->x = btnPlay->x + btnPlay->width + 16;
        btnRec->y = bar->y - (int)btnRec_size.y / 2.0f + (int)bar->height / 2.0f;

        btnJpeg->font = font;
        SDL_Point btnJpeg_size = btnJpeg->setText("JPG");
        btnJpeg->x = btnRec->x + btnRec->width + 16;
        btnJpeg->y = bar->y - (int)btnJpeg_size.y / 2.0f + (int)bar->height / 2.0f;

        if (status_enabled) handle_status(f);

        fade(f);

        for (Widget* widget : widgets)
            widget->handleEvent(e);

        e.type = 0; // consume event
    }
}

}
