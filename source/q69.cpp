#include <iostream>
using namespace std;

int global_val = 100;

void counter() {
    static int count = 5;
    count += 10;
    int global_val = 10;
    cout << count << " " << ::global_val << endl;
}

int main() {
    counter();
    counter();
    return 0;
}
