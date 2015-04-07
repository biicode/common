// Lanza.cpp: implementation of the Lanza class.
//
//////////////////////////////////////////////////////////////////////

#include "lanza.h" 
#include "%GLUT_USER%/glut/include/gl/glut.h" 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Lanza::Lanza()
{
	largo=1.5;
	velocidad.y=20;
	tipo=LANZA;
}

Lanza::~Lanza()
{

}

void Lanza::Dibuja()
{
	glColor3f(1.0f,0.0f,1.0f);

	glDisable(GL_LIGHTING);
	glLineWidth(2.0f);
	glBegin(GL_LINES);
		glVertex3f(posicion.x,posicion.y-largo,0);
		glVertex3f(posicion.x,posicion.y,0);
	glEnd();

	glEnable(GL_LIGHTING);
	glLineWidth(1.0f);
	glPushMatrix();
	glTranslatef(posicion.x,posicion.y,0);
	glRotatef(-90,1,0,0);
   	glutSolidCone(largo/5, largo/2,20 ,1);
	glPopMatrix();

}
