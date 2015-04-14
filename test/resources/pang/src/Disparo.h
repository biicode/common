// Disparo.h: interface for the Disparo class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_disparo_h__57bd1710_790b_4c73_8961_d15173a1be52__included_)
#define afx_disparo_h__57bd1710_790b_4c73_8961_d15173a1be52__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#define NINGUNO				-1
#define GANCHO				0
#define GANCHO_ESPECIAL 	1
#define LANZA				2

#include "vector2d.h" 
#include "objetomovil.h" 

class Disparo  :public ObjetoMovil 
{
public:
	Disparo();
	virtual ~Disparo();	
	
	int GetTipo();	
	virtual void Dibuja()=0;
protected:
	int tipo;
};

#endif // !defined(afx_disparo_h__57bd1710_790b_4c73_8961_d15173a1be52__included_)

