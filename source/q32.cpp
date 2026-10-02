#include <iostream>
using namespace std;

class Counter {
private:
    int count;
public:
    Counter(int c) : count(c) {}
    Counter& operator+=(const Counter& other) {
        this->count += other.count;
        return *this;
    }
    int get() const { return count; }
};

int main() {
    Counter c1(5), c2(3), c3(2);
    (c1 += c2) += c3;
    int x = c1.get();
    cout << x;
    return 0;
}
