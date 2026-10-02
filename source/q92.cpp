#include <iostream>
using namespace std;

int main() {
    int x = 10;
    int y = 20;
    const int* p = &x;
    p = &y;
    cout << *p;
    return 0;
}
