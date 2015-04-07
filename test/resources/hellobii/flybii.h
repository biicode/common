// CoordinadorPang.h: interface for the CoordinadorPang class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(_fly_bii__included_)
#define _fly_bii__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

class FlyBii
{
public:
	FlyBii();
	virtual ~FlyBii(){}

	void Move(float time);
	void Draw();

private:
	float x, y, a, d;


};

#endif

