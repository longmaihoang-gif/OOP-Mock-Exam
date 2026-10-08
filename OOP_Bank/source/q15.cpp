#include <iostream>
using namespace std;

void Print(int x) {
    cout << "Int: " << x;
}

void Print(int x, int y = 10) {
    cout << "Pair: " << x << "," << y;
}

int main() {
    Print(5);
    return 0;
}
