#include <iostream>
using namespace std;

class ArrayHolder {
private:
    int* data;
    int size;
public:
    ArrayHolder(int s) : size(s) {
        data = new int[size];
    }
    ~ArrayHolder() {
        delete[] data;
    }
    ArrayHolder& operator=(const ArrayHolder& other) {
        if (this == &other) return *this;
        delete[] data;
        size = other.size;
        data = new int[size];
        for(int i = 0; i < size; ++i) {
            data[i] = other.data[i];
        }
        return *this;
    }
};

int main() {
    ArrayHolder a1(10);
    ArrayHolder a2(5);
    a2 = a1;
    return 0;
}
