//  pretty.h
//  ❤ ☀ ☆ ☂ ☻ ♞ ☯ ☭ ☢ € → ☎ ❄ ♫ ✂ ▷ ✇ ♎ ⇧ ☮ ♻ ⌘ ⌛ ☘

#include <iostream>
using namespace std;

#include "pretty.h"
#include "hello.h"
%INCLUDE_EXTERNAL_PRETTY%

void prettyHello%BLOCKNAME%(){
	cout<<"* ";
	hello%BLOCKNAME%();
	cout<<" *"<<endl;

	%CALL_EXTERNAL_PRETTY%
}
