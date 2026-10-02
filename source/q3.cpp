#include <iostream>
using namespace std;

class Part {
public:
    Part(int id) { cout << "P" << id; }
    ~Part() { cout << "~P"; }
};

class Device {
    Part p1;
    Part p2;
public:
    Device() : p2(2), p1(1) { cout << "D"; }
    ~Device() { cout << "~D"; }
};

int main() {
    Device dev;
    return 0;
}
