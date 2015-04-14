#pragma once
#include "body.h"
class Cube : public Body
{
protected:
	float side;
public:
	Cube(float s);
	virtual float volume();
};