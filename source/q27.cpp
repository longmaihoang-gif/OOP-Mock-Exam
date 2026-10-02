#include <iostream>
using namespace std;

class Demo {
private:
    int id;
public:
    Demo(int val) : id(val) {
        cout << "C" << id << " ";
    }
    ~Demo() {
        cout << "D" << id << " ";
    }
};

Demo globalObj(0);

void functionScope() {
    Demo localObj3(3);
}

int main() {
    cout << "Start ";
    Demo localObj1(1);
    {
        Demo localObj2(2);
        functionScope();
    }
    cout << "End ";
    return 0;
}
