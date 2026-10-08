#include <iostream>
using namespace std;

class Number {
private:
    int val;
public:
    Number(int v) : val(v) {}
    friend Number operator+(int lhs, const Number& rhs) {
        cout << "Friend+";
        return Number(lhs + rhs.val);
    }
    Number operator+(int rhs) const {
        cout << "Member+";
        return Number(val + rhs);
    }
};

int main() {
    Number n(5);
    Number res1 = n + 10;
    Number res2 = 10 + n;
    return 0;
}
