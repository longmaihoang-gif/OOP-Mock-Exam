#include <iostream>
using namespace std;

void modifyValue(const int* ptr) {
    int* modPtr = // [ĐIỀN CODE TẠI ĐÂY]
    *modPtr = 100;
}

int main() {
    int val = 10;
    modifyValue(&val);
    cout << val;
    return 0;
}
