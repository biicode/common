// GanchoEspecial.cpp: implementation of the GanchoEspecial class.
//
//////////////////////////////////////////////////////////////////////

#include "ganchoespecial.h" 
#include "%GLUT_USER%/glut/include/gl/glut.h" 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

GanchoEspecial::GanchoEspecial()
{
	radio=0.4f;
	velocidad.y=15;
	tipo=GANCHO_ESPECIAL;
}

GanchoEspecial::~GanchoEspecial()
{

}

void GanchoEspecial::Dibuja()
{
	glColor3f(1.0f,1.0f,0.0f);

	glDisable(GL_LIGHTING);
	glLineWidth(2.0f);

	glBegin(GL_LINES);
		glVertex3f(origen.x-0.1,origen.y,0);
		glVertex3f(posicion.x-0.1,posicion.y,0);
		glVertex3f(origen.x+0.1,origen.y,0);
		glVertex3f(posicion.x+0.1,posicion.y,0);
	glEnd();
	glEnable(GL_LIGHTING);
	glLineWidth(1.0f);

	glPushMatrix();
	glTranslatef(posicion.x,posicion.y,0);

   	glutSolidSphere(radio, 20, 20);
	glPopMatrix();
}
