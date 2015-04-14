// CoordinadorPang.h: interface for the CoordinadorPang class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_coordinadorpang_h__708753bc_1ad8_453f_9590_5711aca77b32__included_)
#define afx_coordinadorpang_h__708753bc_1ad8_453f_9590_5711aca77b32__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "mundo.h" 
#include "escenaentrada.h" 
#include "%GLUTAPP_USER%/glutapp/glutapp.h" 

class CoordinadorPang : public GlutApp 
{
public:
	CoordinadorPang();
	virtual ~CoordinadorPang();

	void SpecialKey(unsigned char key);
	void Key(unsigned char key);
	void Timer(float time);
	void Draw();

protected:
	EscenaEntrada entrada;
	Mundo mundo;
	enum Estado {INICIO, JUEGO, GAMEOVER, FIN, PAUSA};
	Estado estado;
};

#endif

