#include <iostream>
using namespace std;

class IntArray {
    int arr[5];
public:
    IntArray() { for (int i = 0; i < 5; i++) arr[i] = i * 10; }
    int operator[](int index) {
        return arr[index];
    }
};

int main() {
    IntArray a;
    a[2] = 99;
    cout << a[2];
    return 0;
}
