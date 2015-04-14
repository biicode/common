// EsferaPulsante.h: interface for the EsferaPulsante class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_esferapulsante_h__90f566e0_255e_4854_b2f4_7967ee677796__included_)
#define afx_esferapulsante_h__90f566e0_255e_4854_b2f4_7967ee677796__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "esfera.h" 

class EsferaPulsante :public Esfera 
{
public:
	Esfera* Dividir();
	void Mueve(float t);
	EsferaPulsante();
	virtual ~EsferaPulsante();

private:
	float radio_max;
	float radio_min;
	float pulso;

};

#endif // !defined(afx_esferapulsante_h__90f566e0_255e_4854_b2f4_7967ee677796__included_)

