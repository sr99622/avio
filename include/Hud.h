#pragma once

#include <SDL.h>
#include "SDL_ttf.h"
#include "Frame.h"
#include "Reader.h"
#include "Writer.h"
#include "Gui.h"

constexpr auto TIMEOUT = 2; // timeout in seconds

namespace avio
{

class Hud
{
public:
	Hud();
	void handleEvent(SDL_Event& e, Frame& f);
	std::string strElapsed(int64_t elapsed) const;
	void showMark(float pct);
	void render(SDL_Renderer* renderer);
	void fade(Frame& f);

	bool heads_up = false;
	bool pin_hud = false;
	bool highlight = false;
	int64_t last_pts = AV_NOPTS_VALUE;

	time_t timeout_start;

	Sint32 last_x = 0;
	Sint32 last_y = 0;
	Sint32 last_click_x = 0;
	Sint32 last_click_y = 0;

	float menu_height = 0.15;
	Uint32 format = 0;
	TTF_Font* font = NULL;

	std::vector<Widget*> widgets;

	ProgressBar* bar = nullptr;
	Label* lblTime = nullptr;
	Label* lblMark = nullptr;
	ButtonRec* btnRec = nullptr;
	ButtonPlay* btnPlay = nullptr;

	Reader* reader = nullptr;
	Writer* writer = nullptr;
	void* display = nullptr;

};

}