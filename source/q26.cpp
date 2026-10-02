#include <iostream>
using namespace std;

class NumberCollection {
private:
    int arr[5];
public:
    NumberCollection() {
        for(int i = 0; i < 5; ++i) arr[i] = i * 10;
    }
    int& operator[](int index) {
        return arr[index];
    }
    int operator()(int multiplier) const {
        int sum = 0;
        for(int i = 0; i < 5; ++i) sum += arr[i] * multiplier;
        return sum;
    }
    operator double() const {
        double sum = 0;
        for(int i = 0; i < 5; ++i) sum += arr[i];
        return sum / 5.0;
    }
};

int main() {
    NumberCollection nc;
    nc[2] = 99;
    cout << nc(2) << " " << double(nc);
    return 0;
}
