#include <iostream>
using namespace std;

void counter() {
    static int count = 0;
    count++;
    cout << count << " ";
}

int main() {
    counter();
    counter();
    counter();
    return 0;
}
