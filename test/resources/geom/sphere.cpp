#include "sphere.h"

Sphere::Sphere(float r):radius(r)
{
}
float Sphere::volume()
{
	return radius*radius*radius;
}
