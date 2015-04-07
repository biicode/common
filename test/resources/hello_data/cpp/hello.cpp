//  hello.h
//  ? ? ? ? ? ? ? ? ? � ? ? ? ? ? ? ? ? ? ? ? ? ? ?
#include "hello.h"

#include <iostream>
#include <fstream>
#include <string>
using namespace std;

void hello%BLOCKNAME%(){
	//bii://data.bmp
	//bii://data.xml
	ifstream f1("%USER%/%BLOCKSIMPLENAME%/data/data.bmp");
	string str;
	getline(f1, str);
	cout<<str<<" ";
	ifstream f2("%USER%/%BLOCKSIMPLENAME%/data/data.xml");
	getline(f2, str);
	cout<<str;
	f1.close();
	f2.close();
}
