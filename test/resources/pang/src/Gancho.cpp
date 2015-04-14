// Gancho.cpp: implementation of the Gancho class.
//
//////////////////////////////////////////////////////////////////////

#include "gancho.h" 
#include "%GLUT_USER%/glut/include/gl/glut.h" 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Gancho::Gancho()
{
	radio=0.25f;
	velocidad.y=8;
	tipo=GANCHO;
}

Gancho::~Gancho()
{

}

void Gancho::Dibuja()
{
	glColor3f(0.0f,1.0f,1.0f);

	glDisable(GL_LIGHTING);
	glBegin(GL_LINES);
		glVertex3f(origen.x,origen.y,0);
		glVertex3f(posicion.x,posicion.y,0);
	glEnd();
	glEnable(GL_LIGHTING);

	glPushMatrix();
	glTranslatef(posicion.x,posicion.y,0);

   	glutSolidSphere(radio, 20, 20);
	glPopMatrix();
}

void Gancho::SetPos(float x, float y)
{
	Disparo::SetPos(x,y);
	origen=posicion;
}
