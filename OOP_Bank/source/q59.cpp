#include <iostream>
using namespace std;

class IntArray {
    int data[2];
public:
    IntArray(int a, int b) {
        data[0] = a; data[1] = b;
    }
    int& operator[](int index) {
        return data[index];
    }
    int operator()(int x) const {
        return data[0] + data[1] + x;
    }
    operator double() const {
        return (data[0] + data[1]) / 2.0;
    }
};

int main() {
    IntArray arr(4, 6);
    arr[0] = 10;
    cout << arr[0] << " ";
    cout << arr(5) << " ";
    double avg = arr;
    cout << avg;
    return 0;
}
