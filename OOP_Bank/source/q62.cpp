#include <iostream>
using namespace std;

int add(int a, int b) {
    return a + b;
}

int main() {
    int x = 10, y = 20;
    const int* p1 = &x;
    int* const p2 = &y;
    
    *p2 = 25;
    p1 = &y;
    
    int (*funcPtr)(int, int) = add;
    
    cout << *p1 << " " << *p2 << " " << funcPtr(3, 4);
    return 0;
}
