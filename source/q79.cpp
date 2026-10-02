#include <iostream>
using namespace std;

void modify(const int* ptr) {
    int* modPtr = const_cast<int*>(ptr);
    *modPtr = 20;
}

int main() {
    const int x = 10;
    modify(&x);
    cout << x;
    return 0;
}
