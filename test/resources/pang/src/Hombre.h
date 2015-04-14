// Hombre.h: interface for the Hombre class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_hombre_h__95914621_f370_4cf8_918e_2e7f98f93d0f__included_)
#define afx_hombre_h__95914621_f370_4cf8_918e_2e7f98f93d0f__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "vector2d.h" 
#include "objetomovil.h" 

class Hombre  :public ObjetoMovil
{
	friend class Interaccion;
public:
	Hombre();
	virtual ~Hombre();
	
	void IncrementaNumBonus();
	void SetNumBonus(int num);
	int GetNumBonus();
	float GetAltura();
	void Dibuja();


protected:
	float altura;
	int num_bonus;
};

#endif // !defined(afx_hombre_h__95914621_f370_4cf8_918e_2e7f98f93d0f__included_)

