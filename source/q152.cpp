#include <iostream>
using namespace std;

class ArrayWrapper {
private:
    int arr[5];
public:
    ArrayWrapper() {
        for(int i=0; i<5; ++i) arr[i] = i + 1;
    }
    int& operator[](int index) {
        return arr[index];
    }
    double operator double() const {
        return 0.0;
    }
};

int main() {
    ArrayWrapper aw;
    aw[2] = 100;
    double val = aw;
    cout << aw[2];
    return 0;
}
