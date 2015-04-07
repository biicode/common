// Interaccion.h: interface for the Interaccion class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_interaccion_h__d2a51b0d_b69f_4823_bead_70ee42098631__included_)
#define afx_interaccion_h__d2a51b0d_b69f_4823_bead_70ee42098631__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "hombre.h" 
#include "caja.h" 
#include "esfera.h" 
#include "disparo.h" 
#include "gancho.h" 
#include "lanza.h" 
#include "bonus.h" 

class Interaccion  
{
public:
	Interaccion();
	virtual ~Interaccion();	
//funciones que modifican (paso por referencia) los objetos que se les pasa como parametro	
	static bool Rebote(Esfera& e, Pared p);
	static void Rebote(Esfera& e, Caja c);
	static void Rebote(Hombre& h, Caja c);
	static bool Rebote(Esfera& e1, Esfera& e2);
	
//funciones de informacion, no cambian los objetos, solo devuelven true si hay colision
	static bool Colision(Esfera e, Hombre h);
	static bool Colision(Gancho d, Pared p);
	static bool Colision(Gancho d, Caja c);
	static bool Colision(Gancho d, Esfera e);
	static bool Colision(Lanza d, Pared p);
	static bool Colision(Lanza d, Caja c);
	static bool Colision(Lanza d, Esfera e);
	static bool Colision(Hombre h, Bonus b);
};

#endif // !defined(afx_interaccion_h__d2a51b0d_b69f_4823_bead_70ee42098631__included_)

