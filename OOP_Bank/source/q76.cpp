#include <iostream>
using namespace std;

class Point {
private:
    int x, y;
public:
    Point(int x, int y) : x(x), y(y) {}
    bool operator==(const Point& other) const {
        return (x == other.x && y == other.y);
    }
    bool operator!=(const Point& other) const {
        return !(*this == other);
    }
};

int main() {
    Point p1(3, 4);
    Point p2(3, 4);
    Point p3(1, 2);
    
    bool res1 = (p1 == p2);
    bool res2 = (p1 != p3);
    
    cout << res1 << " " << res2 << endl;
    return 0;
}
