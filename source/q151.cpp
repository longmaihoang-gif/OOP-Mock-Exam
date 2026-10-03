#include <iostream>
using namespace std;

class Point {
private:
    int x;
public:
    Point(int val) : x(val) {}
    
    friend Point operator+(int val, const Point& p) {
        return Point(val + p.x);
    }
    
    void print() const {
        cout << x;
    }
};

int main() {
    Point p = 5 + Point(10);
    p.print();
    return 0;
}
