#include <iostream>
using namespace std;

class Test {
private:
    int val;
public:
    explicit Test(int x) : val(x) {
        cout << "Exp:" << val << " ";
    }
    int get() const { return val; }
};

void process(Test t) {
    cout << "Proc:" << t.get() << " ";
}

int main() {
    Test t1(10);
    // process(20);
    process(Test(30));
    Test t2 = 40;
    return 0;
}
