#include <iostream>
using namespace std;

class Number {
public:
    int value;
    Number(int v) : value(v) {}
    Number& operator+=(const Number& other) {
        value += other.value;
        return *this;
    }
};

int main() {
    Number x(10);
    Number y(5);
    (x += y) += Number(2);
    cout << x.value << endl;
    return 0;
}
