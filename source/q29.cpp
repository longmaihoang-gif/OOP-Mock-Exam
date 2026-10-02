#include <iostream>
using namespace std;

class Point {
public:
    int x, y;
    Point(int x, int y) : x(x), y(y) {}
};

int main() {
    Point p1(1, 2), p2(1, 2);
    if (p1 == p2) {
        cout << "Equal";
    } else {
        cout << "Not Equal";
    }
    return 0;
}
