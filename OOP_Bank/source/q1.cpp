#include <iostream>
using namespace std;

int Counter(int init) {
    static int count = init;
    count += 2;
    return count;
}

int main() {
    cout << Counter(10) << " ";
    cout << Counter(20) << " ";
    cout << Counter(30);
    return 0;
}
