#include "sphere.h"
#define _USE_MATH_DEFINES
#include <math.h>

Sphere::Sphere(float r):radius(r)
{
}
float Sphere::volume()
{
	return 4./3.*M_PI*radius*radius*radius;
}
