#include <iostream>
#include "@USER_BRL@/geom/sphere.h"
#include "cube.h"

using namespace std;
int main()
{
	Sphere s(2.0f);
	cout<<"Volume: "<<s.volume()<<endl;

	Cube c(3.0f);
	cout<<"Vol Cube: "<<c.volume()<<endl;

	return 1;
}