#include <iostream>
#include "@USER_BRL@/geom/sphere.h"

using namespace std;
int main()
{
	Sphere s(2.0f);
	cout<<"Volume: "<<s.volume()<<endl;

	return 1;
}