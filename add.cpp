
#include <iostream>
#include <string>
using namespace std;

int main(int argc, char** argv) {
    string line;
    while (getline(std::cin, line)) {
        std::cout << std::stoi(line)+1 << std::endl;
    }
}