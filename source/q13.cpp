#include <iostream>
using namespace std;

class Multiplier {
    int factor;
public:
    Multiplier(int f = 1) : factor(f) {}
    int operator()(int val) {
        factor += val;
        return factor;
    }
};

int main() {
    Multiplier m(10);
    cout << m(5) << " ";
    cout << m(5);
    return 0;
}
