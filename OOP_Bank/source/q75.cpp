#include <iostream>
using namespace std;

class Number {
private:
    int value;
public:
    Number(int v) : value(v) {}
    Number operator+(const Number& o) const {
        return Number(value + o.value);
    }
    Number& operator+=(const Number& o) {
        value += o.value;
        return *this;
    }
    int get() const { return value; }
};

int main() {
    Number n1(5);
    Number n2(10);
    Number n3 = n1 + n2;
    n3 += n1;
    cout << n3.get() << endl;
    return 0;
}
