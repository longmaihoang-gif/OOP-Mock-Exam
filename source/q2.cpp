#include <iostream>
using namespace std;

int main() {
    int a = 10;
    int& ref1 = a;
    int& ref2 = 20;
    const int& ref3 = 30;
    cout << ref1 + ref3;
    return 0;
}
