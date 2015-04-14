#include <iostream>
#include "sphere.h"
#include "cube.h"

using namespace std;
int main()
{
	Sphere s(2.0f);	
	s.print();
	cout<<"Volume: "<<s.volume()<<endl;
	
	Cube c(3.0f);
	cout<<"Vol Cube: "<<c.volume()<<endl;

	return 1;
}