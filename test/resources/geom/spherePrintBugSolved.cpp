#include "sphere.h"
#define _USE_MATH_DEFINES
#include <math.h>
#include <iostream>
using namespace std;

Sphere::Sphere(float r):radius(r)
{
}
float Sphere::volume()
{
	return 4./3.*M_PI*radius*radius*radius;
}
void Sphere::print()
{
	cout<<"R: "<<radius<<endl;
}