#include <iostream>
using namespace std;

class Counter {
private:
    int id;
    static int count;
public:
    Counter() {
        count++;
        id = count;
    }
    static int getCount() {
        return count;
    }
    int getId() const {
        return id;
    }
};

int Counter::count = 10;

int main() {
    Counter c1;
    const Counter c2;
    Counter c3;
    cout << Counter::getCount() + c2.getId() + c3.getId();
    return 0;
}
