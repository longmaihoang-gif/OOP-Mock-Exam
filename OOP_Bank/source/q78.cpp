#include <iostream>
using namespace std;

class Number {
private:
    int val;
public:
    Number(int v) : val(v) {}
    Number& operator++() {
        val += 2;
        return *this;
    }
    Number operator++(int) {
        Number temp(*this);
        val += 3;
        return temp;
    }
    int get() const { return val; }
};

int main() {
    Number a(5);
    Number b = ++a;
    Number c = a++;
    cout << b.get() << " " << c.get() << " " << a.get();
    return 0;
}
