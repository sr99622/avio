#include <SDL.h>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <iostream>


namespace avio 
{

class Event
{
public:
    Event() {}

    static std::string pack(const std::vector<SDL_Event>& events);
};

}