#include <iostream>
using namespace std;

class ComplexBuffer {
private:
    int* data;
    size_t size;
public:
    ComplexBuffer(size_t s) : size(s) {
        data = new int[size];
        for(size_t i = 0; i < size; ++i) data[i] = int(i);
    }
    ~ComplexBuffer() {
        delete[] data;
    }
    ComplexBuffer& operator=(const ComplexBuffer& other) {
        if (this == &other) {
            return *this;
        }
        delete[] data;
        size = other.size;
        data = new int[size];
        for(size_t i = 0; i < size; ++i) {
            data[i] = other.data[i];
        }
        return *this;
    }
};

int main() {
    ComplexBuffer a(10);
    ComplexBuffer b(5);
    b = a;
    return 0;
}
