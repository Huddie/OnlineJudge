
#include <iostream>
#include <string>
#include <cstdlib>

using namespace std;

int main(int argc, char** argv) {
    string line;
    while (getline(std::cin, line)) {
        int new_int = std::atoi(line.c_str());
        std::cout << new_int+1 << std::endl;
    }
}