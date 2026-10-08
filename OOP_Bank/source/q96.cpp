#include <iostream>
using namespace std;

class Demo {
private:
    int x;
public:
    Demo(int val) : x(val) {}
    int getX() const {
        return x;
    }
};

int main() {
    const Demo d(10);
    cout << d.getX();
    return 0;
}
