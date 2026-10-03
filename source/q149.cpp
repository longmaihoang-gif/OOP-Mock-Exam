#include <iostream>
using namespace std;

class Box {
private:
    int* ptr;
public:
    Box(int val) {
        ptr = new int(val);
    }
    Box(const Box& other) {
        ptr = new int(*other.ptr);
    }
    ~Box() {
        delete ptr;
    }
    void set(int val) {
        *ptr = val;
    }
    void print() const {
        cout << *ptr << " ";
    }
};

int main() {
    Box b1(10);
    Box b2 = b1;
    b2.set(20);
    b1.print();
    b2.print();
    return 0;
}
