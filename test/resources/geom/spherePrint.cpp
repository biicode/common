#include "sphere.h"
#include <iostream>
using namespace std;

Sphere::Sphere(float r):radius(r)
{
}
float Sphere::volume()
{
	return radius*radius*radius;
}
void Sphere::print()
{
	cout<<"R: "<<radius<<endl;
}