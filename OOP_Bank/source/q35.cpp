#include <iostream>
using namespace std;

class Holder {
    int arr[2];
public:
    Holder(int a, int b) {
        arr[0] = a; arr[1] = b;
    }
    int& operator[](int index) {
        return arr[index];
    }
    operator double() const {
        return (arr[0] + arr[1]) / 2.0;
    }
};

int main() {
    Holder h(10, 20);
    h[0] = 15;
    double avg = h;
    cout << h[0] << " " << avg;
    return 0;
}
