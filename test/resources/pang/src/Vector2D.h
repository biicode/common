// Vector2D.h: interface for the Vector2D class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_vector2d_h__6888fb90_4bfe_421f_9860_72bd24bb8626__included_)
#define afx_vector2d_h__6888fb90_4bfe_421f_9860_72bd24bb8626__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

class Vector2D  
{
public: //atributos
	float x;
	float y;

public: //métodos
	Vector2D(float xv=0.0f,float yv=0.0f); // (1)
	virtual ~Vector2D();

	float modulo();			   // (2) modulo del vector
	float argumento();		   // (3) argumento del vector
	Vector2D Unitario();		   // (4) devuelve un vector unitario
	Vector2D operator - (const Vector2D &)const ;	// (5) resta de vectores
	Vector2D operator + (const Vector2D &)const ;	// (6) suma de vectores
	float operator *(const Vector2D &)const ;	 	// (7) producto escalar
	Vector2D operator *(float)const ;		// (8) producto por un escalar
};


#endif // !defined(afx_vector2d_h__6888fb90_4bfe_421f_9860_72bd24bb8626__included_)

