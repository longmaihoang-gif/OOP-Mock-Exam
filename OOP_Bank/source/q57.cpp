#include <iostream>
using namespace std;

class DataHolder {
public:
    int* val;
    DataHolder(int v) {
        val = new int(v);
    }
    DataHolder(const DataHolder& o) {
        val = new int(*o.val);
    }
    DataHolder& operator=(const DataHolder& o) {
        if (this == &o) return *this;
        delete val;
        val = new int(*o.val);
        return *this;
    }
    ~DataHolder() {
        delete val;
    }
};

int main() {
    DataHolder d1(10);
    DataHolder d2(20);
    d2 = d1;
    *d1.val = 30;
    cout << *d1.val << " " << *d2.val;
    return 0;
}
