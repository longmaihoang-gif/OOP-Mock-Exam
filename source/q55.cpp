#include <iostream>
using namespace std;

class Test {
private:
    int id;
public:
    Test(int n) : id(n) {
        cout << "Init" << id << " ";
    }
    Test(const Test& other) {
        id = other.id + 10;
        cout << "Copy" << id << " ";
    }
    ~Test() {
        cout << "Destroy" << id << " ";
    }
    int getId() const { return id; }
};

Test createTest(Test t) {
    Test temp(t.getId() + 1);
    return temp;
}

int main() {
    Test obj1(1);
    Test obj2 = createTest(obj1);
    return 0;
}
