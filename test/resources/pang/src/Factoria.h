// Factoria.h: interface for the Factoria class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_factoria_h__492f044c_a493_4505_bb6f_e6bf204196bc__included_)
#define afx_factoria_h__492f044c_a493_4505_bb6f_e6bf204196bc__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "hombre.h" 
#include "disparo.h" 
#include "esfera.h" 
#include "caja.h" 

class Factoria  
{
public:
	Factoria();
	virtual ~Factoria();

	static Disparo* CrearDisparo(Hombre h);
	static Esfera* CrearEsfera(Caja c);

};

#endif // !defined(afx_factoria_h__492f044c_a493_4505_bb6f_e6bf204196bc__included_)

