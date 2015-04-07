// ObjetoMovil.h: interface for the ObjetoMovil class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_objetomovil_h__8a0ec6b1_bb12_4aa3_b74a_b80b2b7dc375__included_)
#define afx_objetomovil_h__8a0ec6b1_bb12_4aa3_b74a_b80b2b7dc375__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "vector2d.h" 

class ObjetoMovil  
{
public:
	ObjetoMovil();
	virtual ~ObjetoMovil();
	virtual void Mueve(float t);
	Vector2D GetPos();
	void SetVel(float vx, float vy);
	void SetVel(Vector2D vel);
	virtual void SetPos(float x,float y);
	void SetPos(Vector2D pos);


protected:
	Vector2D posicion;
	Vector2D velocidad;
	Vector2D aceleracion;
};

#endif // !defined(afx_objetomovil_h__8a0ec6b1_bb12_4aa3_b74a_b80b2b7dc375__included_)

