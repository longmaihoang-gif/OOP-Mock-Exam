#include <iostream>
using namespace std;

void testStatic() {
    static int x = 10;
    x += 5;
    cout << x << " ";
}

int main() {
    testStatic();
    testStatic();
    testStatic();
    return 0;
}
