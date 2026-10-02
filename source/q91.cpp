#include <iostream>
using namespace std;

class Number {
private:
    int value;
public:
    explicit Number(int v) : value(v) {
        cout << "Exp:" << value << " ";
    }
    Number(double v) : value(static_cast<int>(v)) {
        cout << "Conv:" << value << " ";
    }
    int get() const { return value; }
};

void process(Number n) {
    cout << "Proc:" << n.get() << " ";
}

int main() {
    Number n1(10);
    process(Number(20));
    Number n3 = 30.5;
    process(n3);
    return 0;
}
