#include <iostream>
using namespace std;

class SmartBuffer {
private:
    int* data;
    size_t size;
public:
    SmartBuffer(size_t s) : size(s) {
        data = new int[size];
    }
    ~SmartBuffer() {
        delete[] data;
    }
    SmartBuffer& operator=(const SmartBuffer& other) {
        cout << "Check self-assignment\n";
        if (this == &other) {
            cout << "Return *this directly\n";
            return *this;
        }
        cout << "Delete old memory\n";
        delete[] data;
        cout << "Allocate new memory & copy\n";
        size = other.size;
        data = new int[size];
        for(size_t i = 0; i < size; ++i) data[i] = other.data[i];
        cout << "Return *this\n";
        return *this;
    }
};

int main() {
    SmartBuffer buf(10);
    buf = buf;
    return 0;
}
