#include <iostream>
#include "sphere.h"

using namespace std;
int main()
{
	Sphere s(2.0f);	
	s.print();
	cout<<"Volume: "<<s.volume()<<endl;
	
	return 1;
}