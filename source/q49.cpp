#include <iostream>
using namespace std;

class Counter {
private:
    int count;
public:
    Counter(c) : count(c) {}
    Counter& operator++() {
        ++count;
        return *this;
    }
    Counter operator++(int) {
        Counter temp = *this;
        count++;
        return temp;
    }
    int get() const { return count; }
};

int main() {
    Counter c(10);
    ++c;
    Counter c2 = c++;
    int z = c.get() + c2.get();
    cout << z;
    return 0;
}
