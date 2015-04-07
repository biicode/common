// EsferaPulsante.cpp: implementation of the EsferaPulsante class.
//
//////////////////////////////////////////////////////////////////////

#include "esferapulsante.h" 

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

EsferaPulsante::EsferaPulsante()
{
	radio_max=2.0f;
	radio_min=0.5f;
	pulso=0.5f;
	aceleracion.y=-4.8f;
	posicion.y=5.0f;
}

EsferaPulsante::~EsferaPulsante()
{

}

void EsferaPulsante::Mueve(float t)
{
	Esfera::Mueve(t);

	if(radio>radio_max)
		pulso=-pulso;
	if(radio<radio_min)
		pulso=-pulso;
	radio+=pulso*t;

	rojo=radio*255;
	verde=255-radio*100;
	azul=100+radio*50;
}

Esfera* EsferaPulsante::Dividir()
{
	if(radio<1.0f)
		return 0; //no dividimos

	pulso*=2.0f;
	if(pulso>10)
		pulso=10;
	//Creamos una esfera nueva, copiando la actual
	Esfera *aux=new EsferaPulsante(*this);
	//Les damos nuevas velocidades
	aux->SetVel(5,8);//a la nueva mitad
	SetVel(-5,8);//a la mitad original
	return aux;
}
