#include <iostream>

using namespace std;

int counter = 5;

void process() {
    static int counter = 2;
    counter++;
    cout << counter << " ";
}

int main() {
    process();
    process();
    cout << ::counter;
    return 0;
}
