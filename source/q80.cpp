#include <iostream>
using namespace std;

class ArrayWrapper {
private:
    int arr[2];
public:
    ArrayWrapper(int a, int b) {
        arr[0] = a; arr[1] = b;
        cout << "Init ";
    }
    int& operator[](int index) {
        cout << "Subscript ";
        return arr[index];
    }
    int operator()(int x) {
        cout << "Functor ";
        return arr[0] + arr[1] + x;
    }
    operator double() const {
        cout << "Cast ";
        return (arr[0] + arr[1]) / 2.0;
    }
};

int main() {
    ArrayWrapper aw(10, 20);
    aw[0] = 5;
    cout << aw(5) << " ";
    double d = aw;
    cout << d;
    return 0;
}
