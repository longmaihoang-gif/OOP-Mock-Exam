#include <iostream>
using namespace std;

class Number {
private:
    int val;
public:
    Number(int v) : val(v) {}
    Number& operator++() {
        ++val;
        return *this;
    }
    Number operator++(int) {
        Number temp(*this);
        val++;
        return temp;
    }
    void print() const { cout << val; }
};

int main() {
    Number n(5);
    Number a = ++n;
    Number b = n++;
    a.print();
    cout << " ";
    b.print();
    cout << " ";
    n.print();
    return 0;
}
