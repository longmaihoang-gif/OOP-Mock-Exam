#include <iostream>
using namespace std;

class Point {
    int x, y;
public:
    Point(int x = 0, int y = 0) : x(x), y(y) {}
    Point operator+(int val) const {
        return Point(x + val, y + val);
    }
    void Print() const { cout << x << " " << y; }
};

int main() {
    Point p1(1, 2);
    Point p2 = p1 + 3;
    Point p3 = 3 + p1;
    p3.Print();
    return 0;
}
