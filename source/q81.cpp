#include <iostream>
using namespace std;

class Buffer {
private:
    int* data;
public:
    Buffer(int val) {
        data = new int(val);
    }
    Buffer(const Buffer& other) {
        data = new int(*other.data);
    }
    ~Buffer() {
        delete data;
    }
    void set(int val) { *data = val; }
    int get() const { return *data; }
};

int main() {
    Buffer b1(10);
    Buffer b2 = b1;
    b2.set(20);
    cout << b1.get() << " " << b2.get();
    return 0;
}
