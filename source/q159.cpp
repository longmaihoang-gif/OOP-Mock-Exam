#include <iostream>
using namespace std;

class Test {
private:
    int val;
public:
    Test(int v) : val(v) {}
    // Copy Constructor
    Test(const Test& t) {
        val = t.val;
        cout << "Copied ";
    }
    int getVal() const { return val; }
};

int main() {
    Test t1(10);
    // [ĐIỀN CODE TẠI ĐÂY]
    cout << t2.getVal();
    return 0;
}
