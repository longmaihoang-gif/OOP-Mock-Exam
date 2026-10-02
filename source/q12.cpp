#include <iostream>
using namespace std;

class Item {
public:
    static int count;
    Item() { count++; }
    ~Item() { count--; }
};

int Item::count = 0;

void Test() {
    Item a, b;
    {
        Item c;
        cout << Item::count << " ";
    }
    cout << Item::count << " ";
}

int main() {
    Test();
    cout << Item::count;
    return 0;
}
