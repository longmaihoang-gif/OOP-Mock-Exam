#include <iostream>
using namespace std;

int main() {
    int* p = new int(10);
    *p += 5;
    cout << *p;
    delete p;
    return 0;
}
