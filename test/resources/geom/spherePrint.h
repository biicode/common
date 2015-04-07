#pragma once

class Sphere
{
protected:
	float radius;
public:
	Sphere(float r);
	float volume();
	void print();
};