#include <iostream>
using namespace std;

class Box {
private:
    int length;
public:
    Box(int l) : length(l) {}
    friend void printLength(const Box& b);
};

void printLength(const Box& b) {
    cout << "Length = " << b.length;
}

int main() {
    Box box(15);
    printLength(box);
    return 0;
}
