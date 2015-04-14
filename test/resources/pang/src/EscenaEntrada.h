// EscenaEntrada.h: interface for the EscenaEntrada class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_escenaentrada_h__a4314577_57f1_434a_acf4_6ce06be060b4__included_)
#define afx_escenaentrada_h__a4314577_57f1_434a_acf4_6ce06be060b4__included_

#include "listaesferas.h" 
#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

class EscenaEntrada  
{
public:
	EscenaEntrada();
	virtual ~EscenaEntrada();

	void RotarOjo();
	void Mueve();
	void Dibuja();

	float x_ojo;
	float y_ojo;
	float z_ojo;
protected:
	ListaEsferas esferas;
};

#endif // !defined(afx_escenaentrada_h__a4314577_57f1_434a_acf4_6ce06be060b4__included_)

