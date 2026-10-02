#include <iostream>
using namespace std;

class Number {
    int val;
public:
    Number(int v) : val(v) {}
    Number& operator++() {
        ++val;
        return *this;
    }
    Number operator++(int) {
        Number temp = *this;
        val++;
        return temp;
    }
    int get() const { return val; }
};

int main() {
    Number n(5);
    Number a = ++n;
    Number b = n++;
    cout << a.get() << " " << b.get() << " " << n.get();
    return 0;
}
