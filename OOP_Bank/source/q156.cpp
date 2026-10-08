#include <iostream>
using namespace std;

class Point {
public:
    int x;
    Point(int val) : x(val) {}
    Point operator+(const Point& p) {
        return Point(x + p.x);
    }
    bool operator==(const Point& p) const {
        return x == p.x;
    }
};

int main() {
    Point p1(10);
    Point p2(20);
    Point p3 = p1 + p2;
    bool res = (p3 == Point(30));
    cout << p3.x << " " << boolalpha << res;
    return 0;
}
