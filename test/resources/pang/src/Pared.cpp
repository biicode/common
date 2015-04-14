// Pared.cpp: implementation of the Pared class.
//
//////////////////////////////////////////////////////////////////////

#include "pared.h" 

#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include <string.h> 
#include <GL/gl.h>
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Pared::Pared()
{
	rojo=verde=azul=255; //blanco
	fondo[0]=0;
}

Pared::~Pared()
{

}

void Pared::Dibuja()
{
	if(fondo[0]==0)
	{
		glDisable(GL_LIGHTING);
		glColor3ub(rojo,verde,azul);
		glBegin(GL_POLYGON);
			glVertex3d(limite1.x,limite1.y,10);
			glVertex3d(limite2.x,limite2.y,10);
			glVertex3d(limite2.x,limite2.y,-10);
			glVertex3d(limite1.x,limite1.y,-10);
		glEnd();
		glEnable(GL_LIGHTING);
	}
	else
	{
		unsigned int textura=OpenGL::LoadTexture(fondo);

		if(textura!=-1)
		{
			glEnable(GL_TEXTURE_2D);
			glBindTexture(GL_TEXTURE_2D,textura); 	
			
			glDisable(GL_LIGHTING);
			glColor3f(1,1,1);
			glBegin(GL_POLYGON);
				glTexCoord2d(0.0,0.0);		glVertex3d(limite1.x,limite1.y,10);
				glTexCoord2d(1,0.0);		glVertex3d(limite2.x,limite2.y,10);
				glTexCoord2d(1,1);			glVertex3d(limite2.x,limite2.y,-10);
				glTexCoord2d(0.0,1);		glVertex3d(limite1.x,limite1.y,-10);
			glEnd();
			glEnable(GL_LIGHTING);
		
			glDisable(GL_TEXTURE_2D);
		}
	}
}
void Pared::SetColor( unsigned char r,unsigned char v, unsigned char a)
{
	rojo=r;
	verde=v;
	azul=a;
}

void Pared::SetPos(float x1, float y1, float x2, float y2)
{
	limite1.x=x1;
	limite1.y=y1;
	limite2.x=x2;
	limite2.y=y2;
}
//Calculo de distancia de una pared a un punto, adicionalmente
//se modifica el valor de un vector direccion opcional que contendrá
//el vector unitario saliente que indica la direccion de la 
//recta más corta entre el punto y la pared.
float Pared::Distancia(Vector2D punto, Vector2D *direccion)
{
	Vector2D u=(punto-limite1);
	Vector2D v=(limite2-limite1).Unitario();
	float longitud=(limite1-limite2).modulo();
	Vector2D dir;
	float valor=u*v;
	float distancia=0;

	if(valor<0)
		dir=u;
	else if(valor>longitud)
		dir=(punto-limite2);
	else
		dir=u-v*valor;
	distancia=dir.modulo();
	if(direccion!=0) //si nos dan un vector…
		*direccion=dir.Unitario();
	return distancia;
}

void Pared::SetFondo(char *f)
{
	strcpy(fondo,f);
}
