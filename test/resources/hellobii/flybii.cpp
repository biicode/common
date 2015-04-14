#include "flybii.h" 
#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include <GL/gl.h>
#include "iostream" 
#include <math.h>

FlyBii::FlyBii()
{
	x=0, y=0;
	a = 0;
	d= 0.075f;
}

void FlyBii::Draw(void){
	//The following comment is necessary to automatically include the resource biilogo.bmp
	//bii://biilogo.bmp
	unsigned int textura=OpenGL::LoadTexture("%HELLOBII_USER%/hellobii/biilogo.bmp");

	glPushMatrix();
	glTranslatef(x,y,0);
	if(textura!=-1)
	{
		glEnable(GL_TEXTURE_2D);
		glBindTexture(GL_TEXTURE_2D,textura); 	
		
		glDisable(GL_LIGHTING);
		glColor3f(1,1,1);
		glBegin(GL_POLYGON);
			glTexCoord2d(0.0,0.0);		glVertex3d(0,0,0);
			glTexCoord2d(1,0.0);		glVertex3d(1.5,0,0);
			glTexCoord2d(1,1);			glVertex3d(1.5,1.5,0);
			glTexCoord2d(0.0,1);		glVertex3d(0,1.5,0);
		glEnd();
		glEnable(GL_LIGHTING);
	
		glDisable(GL_TEXTURE_2D);
	}
	glPopMatrix();
}
void FlyBii::Move(float time){
	a+=d;
	if (a<-5 || a >4) d = -d;
	x= a;
	y= 1.5*sin(a);
}