#pragma once

namespace avio
{


class Border
{
public:
	Border() { left = 0; top = 0; right = 0; bottom = 0; }
	Border(int left, int top, int right, int bottom) :
		left(left), top(top), right(right), bottom(bottom) {}

	int left, top, right, bottom;
};

class Widget
{
public:
	Widget(void* osd) : osd(osd)
	{
		border = Border(4, 4, 4, 4);
	}

	virtual void handleEvent(const SDL_Event& e) {}
	virtual void render(SDL_Renderer* renderer) {}

	virtual bool hovering(const SDL_Event& e)
	{
		if (e.type == SDL_MOUSEMOTION) {
			if ((e.motion.x > x &&
				e.motion.x < x + width &&
				e.motion.y < y + height + 4 &&
				e.motion.y > y - 4))

				hover = true;
			else
				hover = false;

		}
		
		return hover;
	}

	void* osd;

	SDL_Color color_lo = { 178, 178, 178 };
	SDL_Color color_hi = { 255, 255, 255 };
	SDL_Color bar_color_lo = { 0, 178, 178 };
	SDL_Color bar_color_hi = { 0, 255, 255 };

	int x;
	int y;
	int width;
	int height;

	Border border;

	int thickness = 2;
	double font_scale = 0.8f;
	TTF_Font* font = NULL;
	std::string text;
	bool hover = false;
	bool visible = true;

};

class Label : public Widget
{
public:
	Label(void* hud) : Widget(hud) {}
	SDL_Point setText(const std::string& text);
	void render(SDL_Renderer* renderer);

	SDL_Surface* surface = NULL;
	SDL_Texture* texture = NULL;
};

class ButtonRec : public Label
{
public:
	ButtonRec(void* hud) : Label(hud) {}
	void handleEvent(const SDL_Event& e) override;
	void render(SDL_Renderer* renderer) override;
	SDL_Color color = { 0 };
	SDL_Color hot_color_lo = { 178, 0, 0 };
	SDL_Color hot_color_hi = { 255, 0, 0 };
	int last_click_x = -1;
	bool hot = false;
};

class ButtonPlay : public Label
{
public:
	ButtonPlay(void* hud) : Label(hud) {}
	void handleEvent(const SDL_Event& e) override;
	void render(SDL_Renderer* renderer) override;
	SDL_Color color = { 0 };
	SDL_Color hot_color_lo = { 178, 0, 0 };
	SDL_Color hot_color_hi = { 255, 0, 0 };
	int last_click_x = -1;
	bool hot = false;
};

class ProgressBar : public Widget
{
public:
	ProgressBar(void* hud) : Widget(hud) { }
	void handleEvent(const SDL_Event& e) override;
	void render(SDL_Renderer* renderer) override;

	float pct_progress = -101.0f;
	SDL_Color color = { 0 };
	SDL_Color bar_color = { 0 };
	int last_click_x = -1;
	int last_motion_x = -1;
	float mark_pct = 0;
	bool seek_bar_enabled = true;
};

}
