#include <iostream>
using namespace std;

class Box;

class ValueHolder {
private:
    int val;
public:
    ValueHolder(int v) : val(v) {}
    friend int getBoxValue(const Box& b, const ValueHolder& v);
};

class Box {
private:
    int boxVal;
public:
    Box(int bv) : boxVal(bv) {}
    friend int getBoxValue(const Box& b, const ValueHolder& v) {
        return b.boxVal + v.val;
    }
};

int main() {
    Box b(10);
    ValueHolder v(20);
    cout << getBoxValue(b, v);
    return 0;
}
