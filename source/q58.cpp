#include <iostream>
using namespace std;

class Item {
public:
    int id;
    Item(int id) : id(id) {
        cout << "C1 ";
    }
    Item(const Item& other) : id(other.id) {
        cout << "C2 ";
    }
    ~Item() {
        cout << "D ";
    }
};

Item createItem(Item x) {
    return x;
}

int main() {
    Item a(1);
    Item b = createItem(a);
    return 0;
}
