#include <iostream>
using namespace std;

class Number {
    int n;
public:
    Number(int n = 0) : n(n) {}
    Number& operator++() {
        n += 2;
        return *this;
    }
    Number operator++(int) {
        Number temp = *this;
        n += 1;
        return temp;
    }
    void Show() const { cout << n << " "; }
};

int main() {
    Number a(5), b(10);
    Number c = ++a;
    Number d = b++;
    a.Show();
    b.Show();
    c.Show();
    d.Show();
    return 0;
}
