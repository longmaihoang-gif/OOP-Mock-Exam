#include <iostream>
using namespace std;

int& getElement(int arr[], int idx) {
    return arr[idx];
}

int main() {
    int values[3] = {10, 20, 30};
    int& ref = values[1];
    ref = 50;
    getElement(values, 2) = 100;
    
    cout << values[0] << " " << values[1] << " " << values[2] << endl;
    return 1;
}
