// Lanza.h: interface for the Lanza class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_lanza_h__bb823ed6_1188_461c_8586_51e8f7780224__included_)
#define afx_lanza_h__bb823ed6_1188_461c_8586_51e8f7780224__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "disparo.h" 

class Lanza : public Disparo  
{
	friend class Interaccion;
public:
	void Dibuja();
	Lanza();
	virtual ~Lanza();
protected:
	float largo;

};

#endif // !defined(afx_lanza_h__bb823ed6_1188_461c_8586_51e8f7780224__included_)

