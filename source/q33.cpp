#include <iostream>
#include <iostream>
using namespace std;

class Number {
public:
    int value;
    explicit Number(int v) : value(v) {
        cout << "Explicit " << v << " ";
    }
};

void printNumber(Number n) {
    cout << n.value << " ";
}

int main() {
    Number n1 = 10;
    printNumber(20);
    return 0;
}
