#include <iostream>
using namespace std;

class Vector {
private:
    int* data;
    size_t size;
public:
    Vector(size_t s) : size(s) {
        data = new int[size];
        for(size_t i = 0; i < size; ++i) data[i] = int(i + 1);
    }
    ~Vector() {
        delete[] data;
    }
    Vector& operator=(const Vector& other) {
        if (this == &other) return *this;
        delete[] data;
        size = other.size;
        data = new int[size];
        for(size_t i = 0; i < size; ++i) {
            data[i] = other.data[i];
        }
        return *this;
    }
    void print() const {
        for(size_t i = 0; i < size; ++i) cout << data[i] << " ";
        cout << endl;
    }
};

int main() {
    Vector v1(3);
    Vector v2(2);
    v2 = v1;
    v2.print();
    return 0;
}
