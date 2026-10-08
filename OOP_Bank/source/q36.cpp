#include <iostream>
using namespace std;

class Test {
public:
    int x;
    Test(int val) : x(val) { cout << "C" << x << " "; }
    ~Test() { cout << "D" << x << " "; }
};

int main() {
    Test* p = new Test(1);
    {
        Test t(2);
    }
    delete p;
    return 0;
}
