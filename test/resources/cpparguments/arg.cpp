#include <iostream>

int main(int argc, char* argv[])
{
	std::cout << "\nNumber of arguments: " << argc-1 << std::endl;
	for(int i = 1; i<argc; i++)
	{
		std::cout << "argument "<< i <<" is: " << argv[i] << std::endl;
	}
    return 0;
}
