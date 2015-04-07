// Gancho.h: interface for the Gancho class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_gancho_h__c03e1750_7f19_4f92_9727_10e9ec69ac5f__included_)
#define afx_gancho_h__c03e1750_7f19_4f92_9727_10e9ec69ac5f__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "disparo.h" 

class Gancho : public Disparo  
{
	friend class Interaccion;
public:
	void SetPos(float x, float y);
	void Dibuja();
	Gancho();
	virtual ~Gancho();
	float GetRadio(){return radio;}

protected:
	float radio;
	Vector2D origen;
};

#endif // !defined(afx_gancho_h__c03e1750_7f19_4f92_9727_10e9ec69ac5f__included_)

