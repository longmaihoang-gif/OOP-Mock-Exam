#include <iostream>
using namespace std;

class Demo {
private:
    int id;
public:
    Demo(int i) : id(i) { cout << "C" << id << " "; }
    ~Demo() { cout << "D" << id << " "; }
};

Demo globalObj(1);

void functionScope() {
    Demo localObj(2);
}

int main() {
    Demo mainObj(3);
    functionScope();
    return 0;
}
