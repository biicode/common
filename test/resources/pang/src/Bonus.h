// Bonus.h: interface for the Bonus class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_bonus_h__47f74c1d_3000_4fc7_8fda_dea5aa82ecfa__included_)
#define afx_bonus_h__47f74c1d_3000_4fc7_8fda_dea5aa82ecfa__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000
#include "vector2d.h" 
#include "objetomovil.h" 

class Bonus  :public ObjetoMovil
{
	friend class Interaccion;
public:
	void Dibuja();
	Bonus();
	virtual ~Bonus();

private:
	float lado;
};

#endif // !defined(afx_bonus_h__47f74c1d_3000_4fc7_8fda_dea5aa82ecfa__included_)
