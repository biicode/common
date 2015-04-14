// Esfera.cpp: implementation of the Esfera class.
//
//////////////////////////////////////////////////////////////////////

#include "esfera.h" 
#include "%GLUT_USER%/glut/include/gl/glut.h" 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Esfera::Esfera()
{
	rojo=verde=azul=255; //blanco
	radio=1.0f;
	aceleracion.y=-9.8f;
}
Esfera::Esfera(float rad, float x, float y, float vx, float vy)
{
	radio=rad;
	posicion.x=x;
	posicion.y=y;
	velocidad.x=vx;
	velocidad.y=vy;

	rojo=verde=255; 
	azul=100; //color distinto
	aceleracion.y=-9.8;
}

Esfera::~Esfera()
{

}

void Esfera::Dibuja()
{
	glColor3ub(rojo,verde,azul);
	glTranslatef(posicion.x,posicion.y,0);
	glutSolidSphere(radio,20,20);
	glTranslatef(-posicion.x,-posicion.y,0);
}

void Esfera::SetColor( unsigned char r,unsigned char v, unsigned char a)
{
	rojo=r;
	verde=v;
	azul=a;
}
void Esfera::SetRadio(float r)
{
	if(r<0.1F)
		r=0.1F;
	radio=r;
}	


Esfera* Esfera::Dividir()
{
	if(radio<1.0f)
		return 0; //no dividimos

	radio/=2.0f;//Dividimos el radio por 2
	//Creamos una esfera nueva, copiando la actual
	Esfera *aux=new Esfera(*this);
	//Les damos nuevas velocidades
	aux->SetVel(5,8);//a la nueva mitad
	SetVel(-5,8);//a la mitad original
	return aux;

}
