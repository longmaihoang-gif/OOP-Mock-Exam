#include <iostream>
using namespace std;

class Test {
private:
    static int count;
public:
    Test() { count++; }
    static int getCount() {
        return count;
    }
    void display() const {
        cout << "Const Method, Count: " << count << endl;
    }
};

int Test::count = 5;

int main() {
    cout << Test::getCount() << " ";
    const Test t;
    t.display();
    return 0;
}
