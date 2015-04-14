//==============================================================================
// Surface functions
//==============================================================================
#ifndef _CSURFACE_H_
    #define _CSURFACE_H_

#include <%SDL_USER%/sdl/include/SDL.h>

//==============================================================================
class CSurface {
	public:
		CSurface();

	public:
		static SDL_Surface* OnLoad(char* File);

		static bool OnDraw(SDL_Surface* Surf_Dest, SDL_Surface* Surf_Src, int X, int Y);

		static bool OnDraw(SDL_Surface* Surf_Dest, SDL_Surface* Surf_Src, int X, int Y, int X2, int Y2, int W, int H);
};

//==============================================================================

#endif
