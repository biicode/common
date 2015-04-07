#include <iostream>
#include <vector>

enum class Options {None, One, All};

int main(void){
    std::vector<int> v;
    auto total = 0;

    v.push_back(1);
    v.push_back(1);
    v.push_back(1);
    v.push_back(1);

    for( auto d : v ) {
        total += d;
    }

    std::cout << "Total is " << total << std::endl;
}