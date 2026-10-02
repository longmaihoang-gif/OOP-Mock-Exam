#include <iostream>
#include <iostream>
using namespace std;

class Test {
private:
    static int count;
public:
    Test() { count++; }
    static void showCount() const {
        cout << count << endl;
    }
};

int Test::count = 0;

int main() {
    Test t;
    Test::showCount();
    return 0;
}
