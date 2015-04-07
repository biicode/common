//==============================================================================
#include "CApp.h"
#include <iostream>
#include <fstream>

using namespace std;
//==============================================================================

CApp::CApp() {
	Surf_Test = NULL;
	Surf_Display = NULL;

	Running = true;
	b2Vec2 gravity(0.0f, -10.0f);
	world = new b2World(gravity);
	b2BodyDef groundBodyDef;
	groundBodyDef.position.Set(0.0f, -50.0f);
	groundBodyDef.angle = -0.0;

	groundBody[0] = world->CreateBody(&groundBodyDef);
	b2PolygonShape groundBox;
	groundBox.SetAsBox(150.0f, 10.0f);
	groundBody[0]->CreateFixture(&groundBox, 0.0f);

	groundBodyDef.position.Set(0.0f, 0.0f);
	groundBody[1] = world->CreateBody(&groundBodyDef);
	groundBox.SetAsBox(10.0f, 150.0f);
	groundBody[1]->CreateFixture(&groundBox, 0.0f);

	groundBodyDef.position.Set(80.0f, 0.0f);
	groundBody[2] = world->CreateBody(&groundBodyDef);
	groundBox.SetAsBox(10.0f, 150.0f);
	groundBody[2]->CreateFixture(&groundBox, 0.0f);

	for (int i = 0; i < NUM_BICHOS; i++) {
		b2BodyDef bodyDef;
		bodyDef.type = b2_dynamicBody;
		bodyDef.position.Set(i*2, i * 2.0f);
		body[i] = world->CreateBody(&bodyDef);
		b2PolygonShape dynamicBox;
		dynamicBox.SetAsBox(2.5f, 2.5f);
		//dynamicBox=2;
		b2FixtureDef fixtureDef;
		fixtureDef.shape = &dynamicBox;
		fixtureDef.density = 1.0f;
		fixtureDef.friction = 0.6f;
		fixtureDef.restitution = 0.8;
		body[i]->CreateFixture(&fixtureDef);
	}
}
void CApp::OnLoop() {
	float32 timeStep = 1.0f / 60.0f;
	int32 velocityIterations = 6;
	int32 positionIterations = 2;
	//world->Step(timeStep, 1, 1);
	world->Step(timeStep, velocityIterations, positionIterations);
	//	cout<<position.x<<" "<< position.y<<" "<< angle<<endl;
	for (int i = 0; i < NUM_BICHOS; i++) {
		b2Vec2 position = body[i]->GetPosition();
		float32 angle = body[i]->GetAngle();
		x[i] = position.x*10;
		y[i] = 100 - position.y*10;
	}
}
void CApp::OnRender() {
	CSurface::OnDraw(Surf_Display, Surf_Test, 0, 0);
	for (int i = 0; i < NUM_BICHOS; i++) {
		CSurface::OnDraw(Surf_Display, bicho[i], x[i], y[i]);
	}
	SDL_Flip(Surf_Display);

}
void CApp::OnEvent(SDL_Event* Event) {
	CEvent::OnEvent(Event);
}
//==============================================================================
void CApp::OnCleanup() {
	SDL_FreeSurface(Surf_Test);
	SDL_FreeSurface(Surf_Display);
	SDL_Quit();
}
//==============================================================================
void CApp::OnExit() {
	Running = false;
}
void CApp::initWorld() {

}
bool CApp::OnInit() {
	if (SDL_Init(SDL_INIT_EVERYTHING) < 0) {
		return false;
	}

	if ((Surf_Display = SDL_SetVideoMode(800, 600, 32,
			SDL_HWSURFACE | SDL_DOUBLEBUF)) == NULL) {
		return false;
	}
	//bii://bichos/background.bmp
	//bii://bichos/bicho1.bmp
	//bii://bichos/bicho2.bmp
	//bii://bichos/bicho3.bmp
	if ((Surf_Test = CSurface::OnLoad("%BICHOS_USER%/bichos/background.bmp")) == NULL) {
		return false;
	}
	for (int i = 0; i < NUM_BICHOS; i++) {
		char nombre[255];
		if(i%3==0)sprintf(nombre,"%BICHOS_USER%/bichos/bicho1.bmp");
		else if(i%3==1)sprintf(nombre,"%BICHOS_USER%/bichos/bicho2.bmp");
		else sprintf(nombre,"%BICHOS_USER%/bichos/bicho3.bmp");

		if ((bicho[i]= CSurface::OnLoad(nombre)) == NULL) {
			return false;
		}
	}

	return true;
}
//------------------------------------------------------------------------------
int CApp::OnExecute() {
	if (OnInit() == false) {
		return -1;
	}

	SDL_Event Event;

	while (Running) {
		while (SDL_PollEvent(&Event)) {
			OnEvent(&Event);
		}

		OnLoop();
		OnRender();
	}

	OnCleanup();

	return 0;
}

//==============================================================================
int main(int argc, char* argv[]) {
	CApp theApp;

	return theApp.OnExecute();
}
