#include <iostream>
using namespace std;

class Point {
    int x, y;
public:
    Point(int px, int py) : x(px), y(py) {}
    friend ostream& operator<<(ostream& os, const Point& p) {
        os << "(" << p.x << ", " << p.y << ")";
        return os;
    }
};

int main() {
    Point pt(3, 4);
    cout << pt;
    return 0;
}
