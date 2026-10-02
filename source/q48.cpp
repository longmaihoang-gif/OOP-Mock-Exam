#include <iostream>
using namespace std;

class Number {
private:
    int value;
public:
    Number(int v) : value(v) {}
    
    Number& operator++() {
        value += 1;
        return *this;
    }
    
    Number operator++(int) {
        Number temp(*this);
        value += 1;
        return temp;
    }
    
    void show() const { cout << value << " "; }
};

int main() {
    Number n(5);
    Number a = ++n;
    Number b = n++;
    a.show();
    b.show();
    n.show();
    return 0;
}
