#include <iostream>
using namespace std;

class Counter {
private:
    static int count;
    int id;
public:
    Counter() {
        count++;
        id = count;
    }
    int getId() const {
        return id;
    }
    static int getCount() {
        return count;
    }
};

int Counter::count = 10;

int main() {
    const Counter c1;
    Counter c2;
    cout << c1.getId() << " " << Counter::getCount();
    return 0;
}
