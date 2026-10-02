#include <iostream>
using namespace std;

int& GetElement(int arr[], int idx) {
    return arr[idx];
}

int main() {
    int a[3] = {10, 20, 30};
    GetElement(a, 1) = 99;
    cout << a[0] << " " << a[1] << " " << a[2];
    return 0;
}
