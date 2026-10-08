#include <iostream>
using namespace std;

class ArrayHolder {
private:
    int size;
    int* arr;
public:
    ArrayHolder(int s) : size(s) {
        arr = new int[size];
        for(int i=0; i<size; ++i) arr[i] = i + 1;
    }
    ArrayHolder& operator=(const ArrayHolder& other) {
        if (this == &other) {
            cout << "[Self] ";
            return *this;
        }
        delete[] arr;
        size = other.size;
        arr = new int[size];
        for(int i=0; i<size; ++i) {
            arr[i] = other.arr[i];
        }
        cout << "[Copy] ";
        return *this;
    }
    void print() {
        for(int i=0; i<size; ++i) cout << arr[i] << " ";
    }
    ~ArrayHolder() {
        delete[] arr;
    }
};

int main() {
    ArrayHolder a(3);
    ArrayHolder b(2);
    ArrayHolder c(4);
    b = a;
    c = b;
    a = a;
    b.print();
    return 0;
}
