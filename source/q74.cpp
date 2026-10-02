#include <iostream>
using namespace std;

class Box {
public:
    int* val;
    Box(int v) {
        val = new int(v);
    }
    ~Box() {
        delete val;
    }
    Box& operator=(const Box& other) {
        if (this == &other) return *this;
        delete val;
        val = new int(*other.val);
        return *this;
    }
};

int main() {
    Box b1(10);
    Box b2(20);
    b2 = b1;
    *b1.val = 50;
    cout << *b2.val << endl;
    return 0;
}
