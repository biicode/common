// Factoria.cpp: implementation of the Factoria class.
//
//////////////////////////////////////////////////////////////////////

#include "factoria.h" 
#include "ganchoespecial.h" 
#include "lanza.h" 
#include "esferapulsante.h" 
#include <stdlib.h> 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Factoria::Factoria()
{

}

Factoria::~Factoria()
{

}
Disparo* Factoria::CrearDisparo(Hombre h)
{
	Disparo* d=0;
	
	if(h.GetNumBonus()==1)
		d=new GanchoEspecial;
	else if(h.GetNumBonus()>=2)
		d=new Lanza;
	else 
		d=new Gancho;

	Vector2D pos=h.GetPos();
	d->SetPos(pos.x,pos.y);
	
	return d;
}
Esfera* Factoria::CrearEsfera(Caja c)
{
	float alto=c.Alto();
	float ancho=c.Ancho();
	float x=0.7*(-ancho/2+ancho*rand()/(float)RAND_MAX);
	float y=alto/2+alto/2*rand()/(float)RAND_MAX-2;
	float vx=-1+2*rand()/(float)RAND_MAX;
	float vy=-1+2*rand()/(float)RAND_MAX;

	Esfera* e;
	if(rand()%5==0)
		e=new EsferaPulsante;
	else
		e=new Esfera;
	e->SetPos(x,y);
	e->SetVel(vx,vy);
	e->SetColor(rand()%255,rand()%255,rand()%255);
	e->SetRadio(1.0f+rand()/(float)RAND_MAX);

	return e;
}
