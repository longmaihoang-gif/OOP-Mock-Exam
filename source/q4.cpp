#include <iostream>
using namespace std;

class Hero {
public:
    Hero() { cout << "1"; }
    Hero(const Hero&) { cout << "2"; }
    Hero& operator=(const Hero&) { cout << "3"; return *this; }
};

int main() {
    Hero h1;
    Hero h2 = h1;
    Hero h3;
    h3 = h1;
    return 0;
}
