// Esfera.h: interface for the Esfera class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_esfera_h__2e380920_f862_4b76_93c3_ff8a054d6612__included_)
#define afx_esfera_h__2e380920_f862_4b76_93c3_ff8a054d6612__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "vector2d.h" 
#include "objetomovil.h" 

class Esfera  :public ObjetoMovil
{
	friend class Interaccion;
public:
	virtual Esfera* Dividir();
	Esfera();
	Esfera(float rad, float x=0.0f, float y=0.0f, float vx=0.0f, float vy=0.0f);
	virtual ~Esfera();
	
	void Dibuja();
	void SetColor( unsigned char r,unsigned char v, unsigned char a);
	void SetRadio(float r);

protected:
	unsigned char rojo;
	unsigned char verde;
	unsigned char azul;
	float radio;
};

#endif // !defined(afx_esfera_h__2e380920_f862_4b76_93c3_ff8a054d6612__included_)

