#include <iostream>
using namespace std;

class Complex {
private:
    double real;
public:
    Complex(double r = 0) : real(r) {
    }
    Complex operator+(const Complex& c) {
        return Complex(real + c.real);
    }
};int main() {
    Complex c1(3.0);
    Complex c2 = c1 + 4.5;
    Complex c3 = 4.5 + c1;
    return 0;
}
