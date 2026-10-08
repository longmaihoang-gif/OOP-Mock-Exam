#include <iostream>
using namespace std;

int& getElement(int arr[], int idx) {
    return arr[idx];
}

int main() {
    int arr[] = {10, 20, 30};
    getElement(arr, 1) = 99;
    cout << arr[1];
    return 0;
}
