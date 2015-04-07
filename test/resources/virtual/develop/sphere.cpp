#include "sphere.h"

#include <math.h>

Sphere::Sphere(float r):radius(r)
{
}
float Sphere::volume()
{
	return myVolumeDevelop();
}
float Sphere::myVolumeDevelop()
{
	return 4./3.*3.14159*radius*radius*radius;
}