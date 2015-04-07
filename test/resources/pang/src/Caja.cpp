// Caja.cpp: implementation of the Caja class.
//
//////////////////////////////////////////////////////////////////////

#include "caja.h" 
#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include <GL/gl.h>
#include <string.h> 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Caja::Caja()
{
	fondo[0]=0;
	suelo.SetColor(0,100,0);
	suelo.SetPos(-10.0f,0,10.0f,0);

	techo.SetColor(0,100,0);
	techo.SetPos(-10.0f,15.0f,10.0f,15.0f);
	
	pared_dcha.SetColor(0,150,0);
	pared_dcha.SetPos(-10.0f,0,-10.0f,15.0f);

	pared_izq.SetColor(0,150,0);
	pared_izq.SetPos(10.0f,0,10.0f,15.0f);

}

Caja::~Caja()
{

}

void Caja::Dibuja()
{
	suelo.Dibuja();
	techo.Dibuja();
	pared_izq.Dibuja();
	pared_dcha.Dibuja();

	if(fondo[0]==0)
		return;

	unsigned int textura=OpenGL::LoadTexture(fondo);

	if(textura!=-1)
	{
		glEnable(GL_TEXTURE_2D);
		glBindTexture(GL_TEXTURE_2D,textura); 	
		
		glDisable(GL_LIGHTING);
		glColor3f(1,1,1);
		glBegin(GL_POLYGON);
			glTexCoord2d(0.0,0.0);		glVertex3f(-10,0,-10);
			glTexCoord2d(1,0.0);		glVertex3f(10,0,-10);
			glTexCoord2d(1,1);			glVertex3f(10,15,-10);
			glTexCoord2d(0.0,1);		glVertex3f(-10,15,-10);
		glEnd();
		glEnable(GL_LIGHTING);
	
		glDisable(GL_TEXTURE_2D);
	}

}

float Caja::Alto()
{
	return 15.0f;
}

float Caja::Ancho()
{
	return 20.0f;
}

void Caja::SetFondo(char *f)
{
	strcpy(fondo,f);	
}

void Caja::SetFondoParedes(char *f)
{
	pared_dcha.SetFondo(f);
	pared_izq.SetFondo(f);
	techo.SetFondo(f);
	suelo.SetFondo(f);
}
