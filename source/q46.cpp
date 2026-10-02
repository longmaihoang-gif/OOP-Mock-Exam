#include <iostream>
using namespace std;

class Counter {
public:
    static int count;
    Counter() { count++; }
    ~Counter() { count--; }
};

int Counter::count = 0;

void testBlock() {
    Counter c1, c2;
}

int main() {
    Counter c3;
    testBlock();
    cout << Counter::count << endl;
    return 0;
}
