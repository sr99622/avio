#include <chrono>

namespace avio
{

class Clock
{
public:
	uint64_t milliseconds();
	uint64_t update(uint64_t rts);
	uint64_t stream_time();
	int sync(uint64_t rts);
	void pause(bool paused);

	long long correction = 0;

private:
	std::chrono::steady_clock clock;
	bool started = false;
	std::chrono::steady_clock::time_point play_start;
	std::chrono::steady_clock::time_point pause_start;

};

}
