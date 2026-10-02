#include <iostream>
using namespace std;

int* createArray() {
    int* arr = new int[100];
    return arr;
}

int main() {
    int* ptr = createArray();
    // Sử dụng mảng
    delete ptr;
    return 0;
}
