#include <iostream>
using namespace std;

class Potion {
public:
    int power;
    explicit Potion(int p) : power(p) {
        cout << "P" << power << " ";
    }
};

void Drink(Potion p) {
    cout << "D" << p.power << " ";
}

int main() {
    Potion p1(10);
    Potion p2 = Potion(20);
    Drink(static_cast<Potion>(30));
    return 0;
}
