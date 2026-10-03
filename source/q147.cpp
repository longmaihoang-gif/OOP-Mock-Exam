#include <iostream>

using namespace std;

class Number {
private:
    int val;
public:
    Number(int v) : val(v) {}
    
    friend Number operator+(int lhs, const Number& rhs) {
        cout << "F+";
        return Number(lhs + rhs.val);
    }
    
    Number operator+(int rhs) const {
        cout << "M+";
        return Number(this->val + rhs);
    }
};

int main() {
    Number n(10);
    Number a = n + 5;
    Number b = 5 + n;
    return 0;
}
