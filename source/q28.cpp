#include <iostream>
using namespace std;

class Number {
private:
    int val;
public:
    Number(int v = 0) : val(v) {}
    Number operator+(const Number& other) const {
        return Number(this->val + other.val);
    }
    Number& operator+=(const Number& other) {
        this->val += other.val;
        return *this;
    }
    int getVal() const { return val;
    }
};

int main() {
    Number a(5), b(10);
    Number c = a + b;
    c += a;
    cout << c.getVal();
    return 0;
}
