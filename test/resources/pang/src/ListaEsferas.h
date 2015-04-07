// ListaEsferas.h: interface for the ListaEsferas class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_listaesferas_h__4e21ea02_37a6_4454_baa4_9468451f39d3__included_)
#define afx_listaesferas_h__4e21ea02_37a6_4454_baa4_9468451f39d3__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#define MAX_ESFERAS 100

#include "esfera.h" 
#include "caja.h" 
#include "hombre.h" 

class ListaEsferas  
{
public:
	ListaEsferas();
	virtual ~ListaEsferas();

	void Mueve(float t);
	void Dibuja();

	bool Agregar(Esfera* e);
	void Eliminar(Esfera* e);
	void Eliminar(int index);
	void DestruirContenido();

	Esfera* Colision(Hombre h);
	void Rebote(Pared p);
	void Rebote();
	void Rebote(Caja caja);

	int GetNumero(){return numero;}
	Esfera* operator[] (int index);

private:
	Esfera * lista[MAX_ESFERAS];
	int numero;
};

#endif // !defined(afx_listaesferas_h__4e21ea02_37a6_4454_baa4_9468451f39d3__included_)

