#include <iostream>
using namespace std;

class Item {
public:
    Item() { cout << "Def "; }
    Item(const Item&) { cout << "Copy "; }
    ~Item() { cout << "~Item "; }
};

void inspect(const Item& ref) {
    cout << "Ref ";
}

void consume(Item val) {
    cout << "Val ";
}

int main() {
    Item it;
    inspect(it);
    consume(it);
    cout << "End ";
    return 0;
}
