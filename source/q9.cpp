#include <iostream>
using namespace std;

class Fraction {
    int num, den;
public:
    Fraction(int n, int d = 1) : num(n), den(d) {}
    operator double() const {
        return (double)num / den;
    }
};

int main() {
    Fraction f(5, 2);
    double val = f + 1.5;
    cout << val;
    return 0;
}
