#include <iostream>
using namespace std;

class Box {
    int len;
public:
    Box(int l) : len(l) {}
    friend ostream& operator<<(ostream& os, const Box& b) {
        os << b.len;
        return os;
    }
};

int main() {
    Box b1(10), b2(20);
    cout << b1 << " - " << b2;
    return 0;
}
