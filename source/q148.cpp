#include <iostream>
using namespace std;

class IntArray {
private:
    int* data;
public:
    IntArray(int val) {
        data = new int(val);
    }
    IntArray& operator=(const IntArray& other) {
        if (this == &other) return *this;
        delete data;
        data = new int(*other.data);
        return *this;
    }
    ~IntArray() {
        delete data;
    }
    void print() const {
        cout << *data << " ";
    }
};

int main() {
    IntArray a(5);
    IntArray b(10);
    b = a;
    a.print();
    b.print();
    return 0;
}
