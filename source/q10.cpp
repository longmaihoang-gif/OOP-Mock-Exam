#include <iostream>
using namespace std;

class Box {
    int width, height;
public:
    Box(int w, int h) : width(w), height(h) {}
};

int main() {
    Box b1(10, 20);
    Box b2(10, 20);
    if (b1 == b2) {
        cout << "Equal";
    } else {
        cout << "Not Equal";
    }
    return 0;
}
