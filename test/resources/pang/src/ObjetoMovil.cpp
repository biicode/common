// ObjetoMovil.cpp: implementation of the ObjetoMovil class.
//
//////////////////////////////////////////////////////////////////////

#include "objetomovil.h" 

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

ObjetoMovil::ObjetoMovil()
{

}

ObjetoMovil::~ObjetoMovil()
{

}

void ObjetoMovil::Mueve(float t)
{
	posicion=posicion+velocidad*t+aceleracion*(0.5f*t*t);
	velocidad=velocidad+aceleracion*t;
}
Vector2D ObjetoMovil::GetPos()
{
	return posicion;
}
void ObjetoMovil::SetVel(float vx, float vy)
{
	velocidad.x=vx;
	velocidad.y=vy;
}
void ObjetoMovil::SetVel(Vector2D vel)
{
	velocidad=vel;
}
void ObjetoMovil::SetPos(float x,float y)
{
	posicion.x=x;
	posicion.y=y;
}
void ObjetoMovil::SetPos(Vector2D pos)
{
	posicion=pos;
}
