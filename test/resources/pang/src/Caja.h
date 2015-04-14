// Caja.h: interface for the Caja class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_caja_h__d69f6e77_0651_4ef3_84ce_0c1e8a609528__included_)
#define afx_caja_h__d69f6e77_0651_4ef3_84ce_0c1e8a609528__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "pared.h" 

class Caja  
{
	friend class Interaccion;
public:
	void SetFondoParedes(char* f);
	void SetFondo(char* fondo);
	float Ancho();
	float Alto();
	Caja();
	virtual ~Caja();
	void Dibuja();

private:
	Pared suelo;
	Pared techo;
	Pared pared_izq;
	Pared pared_dcha;

protected:
	char fondo[255];
};

#endif // !defined(afx_caja_h__d69f6e77_0651_4ef3_84ce_0c1e8a609528__included_)

