// EscenaEntrada.cpp: implementation of the EscenaEntrada class.
//
//////////////////////////////////////////////////////////////////////

#include "escenaentrada.h" 
#include "factoria.h" 
#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include "%GLUT_USER%/glut/include/gl/glut.h" 
#include <math.h> 
#include <stdlib.h> 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

EscenaEntrada::EscenaEntrada()
{
	x_ojo=0;
	y_ojo=7.5;
	z_ojo=30;
		
}

EscenaEntrada::~EscenaEntrada()
{

}
void EscenaEntrada::RotarOjo()
{
	float dist=sqrt(x_ojo*x_ojo+z_ojo*z_ojo);
	float ang=atan2(z_ojo,x_ojo);
	ang+=0.02f;
	x_ojo=dist*cos(ang);
	z_ojo=dist*sin(ang);
}
void EscenaEntrada::Dibuja()
{
	gluLookAt(x_ojo, y_ojo, z_ojo,  // posicion del ojo
			0.0, y_ojo, 0.0,      // hacia que punto mira  (0,0,0) 
			0.0, 1.0, 0.0);      // definimos hacia arriba (eje Y)    

	//aqui es donde hay que poner el codigo de dibujo
	//bii://entrada.bmp
	unsigned int textura=OpenGL::LoadTexture("%USER%/pang/bin/entrada.bmp");
	if(textura!=-1)
	{
		glEnable(GL_TEXTURE_2D);
		glBindTexture(GL_TEXTURE_2D,textura); 			
		glDisable(GL_LIGHTING);
		glColor3ub(255,255,255);
		
		glColor3f(1,1,1);
		glBegin(GL_POLYGON);
			glTexCoord2d(0.0,0.0);		glVertex3f(-10,0,-3);
			glTexCoord2d(1,0.0);		glVertex3f(10,0,-3);
			glTexCoord2d(1,1);			glVertex3f(10,15,-3);
			glTexCoord2d(0.0,1);		glVertex3f(-10,15,-3);
		glEnd();

		glEnable(GL_LIGHTING);	
		glDisable(GL_TEXTURE_2D);
	}
	//bii://agua.bmp
	textura=OpenGL::LoadTexture("%USER%/pang/bin/agua.bmp");
	if(textura!=-1)
	{
		glEnable(GL_TEXTURE_2D);
		glBindTexture(GL_TEXTURE_2D,textura); 			
		glDisable(GL_LIGHTING);
		glColor3ub(255,255,255);
	
		GLUquadricObj * qobj=gluNewQuadric();
		gluQuadricTexture  (qobj , GL_TRUE );
		gluSphere(qobj,42,15,15);
		gluDeleteQuadric(qobj);

		glEnable(GL_LIGHTING);	
		glDisable(GL_TEXTURE_2D);
	}
	
	esferas.Dibuja();

}

void EscenaEntrada::Mueve()
{
	RotarOjo();
	esferas.Mueve(0.025f);
	esferas.Rebote();
	Caja c;
	esferas.Rebote(c);

	if(rand()%30==0)
	{
		Esfera* e=Factoria::CrearEsfera(c);
		e->SetVel(-10+rand()%20,rand()%20);
		esferas.Agregar(e);
	}

	if(esferas.GetNumero()>10)
		esferas.DestruirContenido();
}
