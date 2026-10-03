#include <iostream>
using namespace std;

class NumberHolder {
private:
    int value;
public:
    NumberHolder(int v) : value(v) {
        cout << "Init;";
    }
    operator double() const {
        cout << "Conv;";
        return value;
    }
    int operator()(int multiplier) {
        cout << "Func;";
        return value * multiplier;
    }
};

int main() {
    NumberHolder nh(5);
    double d = nh;
    int res = nh(3);
    return 0;
}
