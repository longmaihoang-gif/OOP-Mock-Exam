#include <iostream>
using namespace std;

class Test {
public:
    int x;
    // Cố gắng nạp chồng toán tử chấm .
    int operator.(Test& t) {
        return t.x;
    }
};

int main() {
    Test t;
    t.x = 10;
    cout << t.x;
    return 0;
}
