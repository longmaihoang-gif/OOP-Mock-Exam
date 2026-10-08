#include <iostream>

using namespace std;

class Item {
private:
    const int code;
    static int count;
public:
    Item(int c) : code(c) {
        count += c;
    }
    static int getCount() {
        return count;
    }
    int getCode() const {
        return code;
    }
};

int Item::count = 10;

int main() {
    Item i1(5);
    const Item i2(15);
    Item::getCount();
    Item i3(10);
    cout << Item::getCount() << "-" << i3.getCode() << endl;
    return 0;
}
