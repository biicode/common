// Pared.h: interface for the Pared class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_pared_h__bb718927_23bc_4329_93c1_c5a28d5d9cc3__included_)
#define afx_pared_h__bb718927_23bc_4329_93c1_c5a28d5d9cc3__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "vector2d.h" 

class Pared  
{
	friend class Interaccion;
public:
	void SetFondo(char* f);
	Pared();
	virtual ~Pared();
	void Dibuja();
	void SetColor( unsigned char r,unsigned char v, unsigned char a);
	void SetPos(float x1,float y1,float x2, float y2);
	float Distancia(Vector2D punto, Vector2D *direccion=0);

private:	
	Vector2D limite1;
	Vector2D limite2;
	unsigned char rojo;
	unsigned char verde;
	unsigned char azul;
protected:
	char fondo[255];
};

#endif // !defined(afx_pared_h__bb718927_23bc_4329_93c1_c5a28d5d9cc3__included_)

