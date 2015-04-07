#pragma once

#include "body.h"

class Sphere : public Body
{
protected:
	float radius;
public:
	Sphere(float r);
	virtual float volume();
};