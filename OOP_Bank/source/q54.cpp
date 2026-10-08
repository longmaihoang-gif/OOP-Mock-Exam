#include <iostream>
using namespace std;

class Demo {
public:
    int x;
    Demo(int val) : x(val) { cout << "C" << x << " "; }
    ~Demo() { cout << "D" << x << " "; }
};

void test() {
    Demo d1(1);
    {
        Demo d2(2);
    }
    Demo d3(3);
}

int main() {
    test();
    return 0;
}
