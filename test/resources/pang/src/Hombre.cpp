// Hombre.cpp: implementation of the Hombre class.
//
//////////////////////////////////////////////////////////////////////

#include "hombre.h" 

#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include <GL/gl.h>
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Hombre::Hombre()
{
	altura=1.8f;
	num_bonus=0;
}

Hombre::~Hombre()
{

}

void Hombre::Dibuja()
{
	glPushMatrix();
	glTranslatef(posicion.x,posicion.y,0);



	//bii://hombre.bmp
	unsigned int textura=OpenGL::LoadTexture("%USER%/pang/bin/hombre.bmp");

	if(textura!=-1)
	{
		glEnable(GL_TEXTURE_2D);
		glBindTexture(GL_TEXTURE_2D,textura); 	
		
		glDisable(GL_LIGHTING);
		glColor3f(1,1,1);
		glBegin(GL_POLYGON);
			glTexCoord2d(0.0,0.0);		glVertex3f(-1,0,0);
			glTexCoord2d(1,0.0);		glVertex3f(1,0,0);
			glTexCoord2d(1,1);			glVertex3f(1,altura,0);
			glTexCoord2d(0.0,1);		glVertex3f(-1,altura,0);
		glEnd();
		glEnable(GL_LIGHTING);
	
		glDisable(GL_TEXTURE_2D);
	}
	
	glPopMatrix();

}

float Hombre::GetAltura()
{
	return altura;
}

int Hombre::GetNumBonus()
{
	return num_bonus;
}

void Hombre::SetNumBonus(int num)
{
	num_bonus=num;
}

void Hombre::IncrementaNumBonus()
{
	num_bonus++;
}
