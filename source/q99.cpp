#include <iostream>
using namespace std;

class Number {
private:
    int val;
public:
    Number(int v) : val(v) {}
    
    // Hậu tố ++
    Number operator++(int) {
        Number temp = *this;
        val++;
        return temp;
    }
};

int main() {
    Number n(5);
    n++;
    return 0;
}
