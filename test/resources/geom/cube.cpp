#include "cube.h"

Cube::Cube(float s):side(s)
{
}
float Cube::volume()
{
	return side*side;
}
