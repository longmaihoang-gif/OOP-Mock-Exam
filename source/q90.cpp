#include <iostream>
using namespace std;

int counter() {
    static int count = 0;
    count++;
    return count;
}

int main() {
    cout << counter() << " ";
    cout << counter() << " ";
    cout << count << endl;
    return 0;
}
