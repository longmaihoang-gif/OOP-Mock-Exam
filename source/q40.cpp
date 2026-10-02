#include <iostream>
using namespace std;

class MathVector {
private:
    int data[5];
public:
    MathVector() {
        for(int i = 0; i < 5; ++i) data[i] = i + 1;
    }
    
    int& operator[](int index) {
        return data[index];
    }
    
    int operator()(int multiplier) const {
        int sum = 0;
        for(int i = 0; i < 5; ++i) {
            sum += data[i] * multiplier;
        }
        return sum;
    }
    
    operator double() const {
        double total = 0;
        for(int i = 0; i < 5; ++i) total += data[i];
        return total / 5.0;
    }
};

int main() {
    MathVector mv;
    mv[2] = 10;
    int result = mv(3);
    double avg = mv;
    cout << mv[2] << " " << result << " " << avg << endl;
    return 0;
}
