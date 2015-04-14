// ListaEsferas.cpp: implementation of the ListaEsferas class.
//
//////////////////////////////////////////////////////////////////////

#include "listaesferas.h" 
#include "interaccion.h" 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

ListaEsferas::ListaEsferas()
{
	numero=0;
	for(int i=0;i<MAX_ESFERAS;i++)
		lista[i]=0;

}

ListaEsferas::~ListaEsferas()
{

}

bool ListaEsferas::Agregar(Esfera *e)
{
	for(int i=0;i<numero;i++)//para evitar que se añada una esfera ya existente
		if(lista[i]==e)
			return false;

	if(numero<MAX_ESFERAS)
	   lista[numero++]=e;
	else 
		return false;
	return true;
}

void ListaEsferas::Dibuja()
{
	for(int i=0;i<numero;i++)
		lista[i]->Dibuja();
}

void ListaEsferas::Mueve(float t)
{
	for(int i=0;i<numero;i++)
		lista[i]->Mueve(t);
}


void ListaEsferas::Rebote(Caja caja)
{
	for(int i=0;i<numero;i++)
		Interaccion::Rebote(*(lista[i]),caja);

}

void ListaEsferas::Rebote()
{
	for(int i=0;i<numero-1;i++)
		for(int j=i+1;j<numero;j++)
			Interaccion::Rebote(*(lista[i]),*(lista[j]));
}

void ListaEsferas::Rebote(Pared p)
{
	for(int i=0;i<numero;i++)
		Interaccion::Rebote(*(lista[i]),p);
}

void ListaEsferas::DestruirContenido()
{
	for(int i=0;i<numero;i++)
		delete lista[i];

	numero=0;
}

void ListaEsferas::Eliminar(int index)
{
	if((index<0)||(index>=numero))
		return;
	
	delete lista[index];

	numero--;
	for(int i=index;i<numero;i++)
		lista[i]=lista[i+1];

}

void ListaEsferas::Eliminar(Esfera *e)
{
	for(int i=0;i<numero;i++)
  		if(lista[i]==e)
		{
	  		Eliminar(i);
	  		return;
		}

}

Esfera* ListaEsferas::Colision(Hombre h)
{
	for(int i=0;i<numero;i++)
	{
		if(Interaccion::Colision(*(lista[i]),h))
			return lista[i];
	}
	return 0; //no hay colisión

}
Esfera *ListaEsferas::operator [](int i)
{
	if(i>=numero)
		i=numero-1;
	if(i<0)
		i=0;
	
	return lista[i];
}
