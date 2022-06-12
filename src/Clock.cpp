#include "Clock.h"
#include <iostream>

constexpr auto MAX_CLOCK_DIFF = 1000;

namespace avio
{

	uint64_t Clock::milliseconds()
{
	if (!started) {
		play_start = clock.now();
		started = true;
	}
	auto current = clock.now();
	return std::chrono::duration_cast<std::chrono::milliseconds>(current - play_start).count();
}

uint64_t Clock::stream_time()
{
	if (!started) {
		play_start = clock.now();
		started = true;
	}

	return milliseconds() - correction;
}

uint64_t Clock::update(uint64_t rts)
{
	if (!started) {
		play_start = clock.now();
		started = true;
	}

	uint64_t current = milliseconds() - correction;

	if (current > rts) {
		uint64_t diff = current - rts;
		if (diff > MAX_CLOCK_DIFF) {
			correction -= (rts - current);
		}
		return 0;
	}
	else {
		uint64_t diff = rts - current;
		if (diff > MAX_CLOCK_DIFF) {
			correction += (current - rts);
			diff = 0;
		}
		return diff;
	}
}

int Clock::sync(uint64_t rts)
{
	if (!started) {
		play_start = clock.now();
		started = true;
	}

	uint64_t current = milliseconds() - correction;
	int diff = rts - current;
	correction -= diff;
	return diff;
}

void Clock::pause(bool paused)
{
	if (paused) {
		pause_start = clock.now();
	}
	else {
		auto current = clock.now();
		correction += std::chrono::duration_cast<std::chrono::milliseconds>(current - pause_start).count();
	}
}

}