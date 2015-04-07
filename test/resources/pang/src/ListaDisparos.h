// ListaDisparos.h: interface for the ListaDisparos class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_listadisparos_h__b84e82d8_c6da_4622_94a9_4b57446dcec3__included_)
#define afx_listadisparos_h__b84e82d8_c6da_4622_94a9_4b57446dcec3__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#define MAX_DISPAROS 3
#include "disparo.h" 
#include "caja.h" 

class ListaDisparos  
{
public:
	ListaDisparos();
	virtual ~ListaDisparos();
	
	bool Agregar(Disparo* d);
	void DestruirContenido();
	void Eliminar(Disparo* d);
	void Eliminar(int index);

	void Mueve(float t);
	void Dibuja();

	void Colision(Pared p);
	void Colision(Caja c);

	int GetNumero(){return numero;}
	Disparo* operator[] (int index);

private:
	Disparo * lista[MAX_DISPAROS];
	int numero;
};

#endif // !defined(afx_listadisparos_h__b84e82d8_c6da_4622_94a9_4b57446dcec3__included_)

