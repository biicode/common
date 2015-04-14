#include "%GLUTAPP_USER%/glutapp/glutapp.h" 
#include "iostream" 

#include <math.h>
#include "flybii.h"
#include <GL/glu.h>

using namespace std;

class MyGlutApp: public GlutApp
{
public:
	MyGlutApp(string name):GlutApp(name){
		
	}
	void Draw(void)
	{
		gluLookAt(0, 0, 10,  // posicion del ojo
			0.0, 0, 0.0,      // hacia que punto mira  (0,0,0) 
			0.0, 1.0, 0.0);      // definimos hacia arriba (eje Y)  
		bii.Draw();
	}
	void Timer(float time)
	{
		bii.Move(time);
	}
private:
	FlyBii bii;
	
};

int main(int argc,char* argv[])
{
	MyGlutApp myApp("Hello Bii");
	myApp.Run();
	return 0;   
}


