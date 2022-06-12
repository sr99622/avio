#include "Hud.h"
#include "Gui.h"
#include "Display.h"

namespace avio
{

SDL_Point Label::setText(const std::string& text)
{
	this->text = text;
	int base = 0;

	surface = TTF_RenderText_Blended(font, text.c_str(), color_lo);
	width = surface->w;
	height = surface->h;
	SDL_Point result = { width, height };
	return result;
}

void Label::render(SDL_Renderer* renderer)
{
	if (!visible) return;
	texture = SDL_CreateTextureFromSurface(renderer, surface);
	SDL_Rect rect = { x, y, width, height };
	SDL_RenderCopy(renderer, texture, NULL, &rect);
	SDL_DestroyTexture(texture);
}

void ButtonRec::render(SDL_Renderer* renderer)
{
	if (!visible) return;
	texture = SDL_CreateTextureFromSurface(renderer, surface);
	SDL_Rect rect = { x, y, width, height };
	SDL_RenderCopy(renderer, texture, NULL, &rect);
	SDL_DestroyTexture(texture);
	rect.w += 8;
	rect.x -= 4;
	SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, SDL_ALPHA_OPAQUE);
	SDL_RenderDrawRect(renderer, &rect);
}

void ButtonRec::handleEvent(const SDL_Event& e)
{
	surface = TTF_RenderText_Blended(font, text.c_str(), color);
	if (hovering(e)) {
		if (e.type == SDL_MOUSEBUTTONDOWN) {
			if (e.button.button == SDL_BUTTON_LEFT) {
				Display* display = (Display*)((Hud*)hud)->display;
				display->toggleRecord();
			}
		}
	}

	if (hot)
		color = (hovering(e) ? hot_color_hi : hot_color_lo);
	else
		color = (hovering(e) ? color_hi : color_lo);
}

void ButtonPlay::render(SDL_Renderer* renderer)
{
	if (!visible) return;
	texture = SDL_CreateTextureFromSurface(renderer, surface);
	SDL_Rect rect = { x, y, width, height };
	SDL_RenderCopy(renderer, texture, NULL, &rect);
	SDL_DestroyTexture(texture);
	rect.w += 8;
	rect.x -= 4;
	SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, SDL_ALPHA_OPAQUE);
	SDL_RenderDrawRect(renderer, &rect);
}

void ButtonPlay::handleEvent(const SDL_Event& e)
{
	text = (hot) ? ">" : "||";
	color = (hovering(e) ? color_hi : color_lo);

	surface = TTF_RenderText_Blended(font, text.c_str(), color);
	if (hovering(e)) {
		if (e.type == SDL_MOUSEBUTTONDOWN) {
			if (e.button.button == SDL_BUTTON_LEFT) {
				Display* display = (Display*)((Hud*)hud)->display;
				display->togglePause();
				//hot = !hot;
			}
		}
	}
}

void ProgressBar::handleEvent(const SDL_Event& e)
{
	color = (hovering(e) ? color_hi : color_lo);
	bar_color = (hovering(e) ? bar_color_hi : bar_color_lo);
	if (hovering(e)) {
		if (e.type == SDL_MOUSEMOTION) {
			mark_pct = (e.motion.x - x) / (float)width;
		}
		if (e.type == SDL_MOUSEBUTTONDOWN) {
			if (e.button.button == SDL_BUTTON_LEFT) {
				if (e.button.x != last_click_x) {
					float pct = (e.button.x - x) / (float)width;
					last_click_x = e.button.x;
					((Hud*)hud)->reader->request_seek(pct);
				}
			}
		}
		((Hud*)hud)->showMark(mark_pct);
	}
	else {
		((Hud*)hud)->lblMark->visible = false;
	}
}

void ProgressBar::render(SDL_Renderer* renderer)
{
	if (!visible) return;
	if (pct_progress < -100.0f) return;

	SDL_Point bar_start = { x, y };
	SDL_Point bar_end = { x + width, y };
	SDL_Point elapsed = { (int)(x + width * pct_progress), y };

	SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, SDL_ALPHA_OPAQUE);
	for (int i = 0; i < height; i++)
		SDL_RenderDrawLine(renderer, bar_start.x, bar_start.y + i, bar_end.x, bar_end.y + i);

	SDL_SetRenderDrawColor(renderer, bar_color.r, bar_color.g, bar_color.b, SDL_ALPHA_OPAQUE);
	for (int i = 0; i < height; i++)
		SDL_RenderDrawLine(renderer, bar_start.x, bar_start.y + i, elapsed.x, elapsed.y + i);

}

}
