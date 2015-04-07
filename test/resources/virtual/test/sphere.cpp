#include "sphere.h"
#include <math.h>
#include <iostream>

using namespace std;

Sphere::Sphere(float r):radius(r)
{
	
}
float Sphere::volume()
{
	return myVolumeTest();
}
float Sphere::myVolumeTest()
{
    return 4./3.*3.14159*radius*radius*radius+100;
}