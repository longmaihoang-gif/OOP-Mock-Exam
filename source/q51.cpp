#include <iostream>
using namespace std;

class Value {
private:
    int val;
public:
    Value(int v = 0) : val(v) {}
    Value& operator+=(const Value& other) {
        this->val += other.val;
        return *this;
    }
    int get() const { return val; }
};

int main() {
    Value a(10), b(5), c(2);
    a += (b += c);
    cout << a.get() << " " << b.get() << " " << c.get();
    return 0;
}
