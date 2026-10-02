#include <iostream>
using namespace std;

class Test {
public:
    int id;
    Test(int i) : id(i) { cout << "C" << id << " "; }
    ~Test() { cout << "D" << id << " "; }
};

int main() {
    Test t1(1);
    {
        Test t2(2);
    }
    return 0;
}
