// CoordinadorPang.h: interface for the CoordinadorPang class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(_glut_app__included_)
#define _glut_app__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include <string>
using namespace std;

//singleton, do not create more than one per application
class GlutApp 
{
public:
	GlutApp(string name);
	virtual ~GlutApp(){}

	//Provide your own functions
	virtual void SpecialKey(unsigned char key){}
	virtual void Key(unsigned char key){}
	virtual void Timer(float time){}
	virtual void Draw(){}

	void Run();
private:

	

};

#endif

