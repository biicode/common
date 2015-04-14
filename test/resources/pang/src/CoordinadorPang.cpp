// CoordinadorPang.cpp: implementation of the CoordinadorPang class.
//
//////////////////////////////////////////////////////////////////////

#include "coordinadorpang.h" 
#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include <stdlib.h> 
#include "iostream" 

using namespace std;
//#include <windows.h> 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CoordinadorPang::CoordinadorPang():GlutApp("Pang")
{
	estado=INICIO;
}

CoordinadorPang::~CoordinadorPang()
{
	OpenGL::DeleteTextures();
}
void CoordinadorPang::SpecialKey(unsigned char key)
{
	if(estado==JUEGO)
		mundo.TeclaEspecial(key);
}
void CoordinadorPang::Key(unsigned char key)
{
	if(estado==INICIO)
	{
		if(key=='e')
		{
			mundo.Inicializa();
			//bii://testmusic.wav
			//PlaySound("%USER%/pang/bin/testmusic.wav",NULL,SND_FILENAME |SND_ASYNC |SND_LOOP );
			estado=JUEGO;
		}
		if(key=='s')
			exit(0);
	}
	else if(estado==JUEGO)
	{
		if(key=='p')
		{
			estado=PAUSA;
		}
		mundo.Tecla(key);
	}
	else if(estado==GAMEOVER)
	{
		if(key=='c')
			estado=INICIO;
	}
	else if(estado==FIN)
	{
		if(key=='c')
			estado=INICIO;
	}
	else if(estado==PAUSA)
	{
		if(key=='c')
			estado=JUEGO;
	}
}
void CoordinadorPang::Timer(float time)
{
	if(estado==INICIO)
		entrada.Mueve();
	else if(estado==JUEGO)
	{
		mundo.Mueve();
		if(mundo.GetNumEsferas()==0)
		{
			if(!mundo.CargarNivel())
			{
		//		PlaySound("Aplauso.wav",NULL,SND_FILENAME |SND_ASYNC );
				estado=FIN;
			}
		}
		if(mundo.Impacto())
		{
			estado=GAMEOVER;
	//		PlaySound("Golpe.wav",NULL,SND_FILENAME |SND_ASYNC );
		}
	}
}
void CoordinadorPang::Draw()
{
	if(estado==INICIO)
	{
		entrada.Dibuja();
		OpenGL::PrintText("Pang 1.0.",0,0,255,255,255);
		OpenGL::PrintText("by Rodriguez-Losada & Hernando",0,20,155,255,0);
		OpenGL::PrintText("Copyright 2009. Todos los derechos reservados",0,40,155,255,0);
		OpenGL::PrintText("Pulse tecla -E- para empezar",0,60,5,255,255);
		OpenGL::PrintText("Pulse tecla -S- para salir",0,80,5,255,255);
	}
	else if(estado==JUEGO)
		mundo.Dibuja();
	else if(estado==GAMEOVER)
	{
		mundo.Dibuja();
		OpenGL::PrintText("GAMEOVER: Has perdido",0,0,255,255,255);
		OpenGL::PrintText("Pulsa -C- para continuar",0,20,155,255,0);
	}
	else if(estado==FIN)
	{
		mundo.Dibuja();
		OpenGL::PrintText("ENHORABUENA, Has triunfado!",0,0,255,255,255);
		OpenGL::PrintText("Pulsa -C- para continuar",0,20,155,255,0);
	}
	else if(estado==PAUSA)
	{
		mundo.Dibuja();
		OpenGL::PrintText("JUEGO PAUSADO",0,0,255,255,255);
		OpenGL::PrintText("Pulsa -C- para continuar",0,20,155,255,0);
	}
}
