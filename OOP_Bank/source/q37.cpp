#include <iostream>
using namespace std;

class Demo {
public:
    Demo() { cout << "Default "; }
    Demo(int x) { cout << "Param " << x << " "; }
    Demo(const Demo& other) { cout << "Copy "; }
    ~Demo() { cout << "Destruct "; }
};

void func(Demo d) {
    cout << "Func ";
}

int main() {
    Demo d1;
    Demo d2(5);
    func(d1);
    return 0;
}
