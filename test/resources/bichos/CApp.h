//==============================================================================
// SDL Tutorial 1
//==============================================================================
#ifndef _CAPP_H_
#define _CAPP_H_

#include "%BOX2D_USER%/box2d/Box2D.h"

#include <%SDL_USER%/sdl/include/SDL.h>

#include "CEvent.h"
#include "CSurface.h"

#define NUM_BICHOS 20

class CApp: public CEvent {
	b2World * world;
	int num_bichos;
	b2Body* body[NUM_BICHOS];
	b2Body* groundBody[3];
private:
	bool Running;
	SDL_Surface* Surf_Display;
	SDL_Surface* Surf_Test;
	SDL_Surface* bicho[NUM_BICHOS];
	SDL_Surface* aux;

	float x[NUM_BICHOS],y[NUM_BICHOS];
	unsigned int texture;
public:
	CApp();
	int OnExecute();

public:
	bool OnInit();
	void OnEvent(SDL_Event* Event);
	void OnExit();
	void OnLoop();
	void OnRender();
	void OnCleanup();
	void initWorld();


};

//==============================================================================

#endif
