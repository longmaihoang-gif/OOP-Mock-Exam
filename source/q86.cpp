#include <iostream>
using namespace std;

class MathBox {
private:
    int values[3];
public:
    MathBox(int a, int b, int c) {
        values[0] = a;
        values[1] = b;
        values[2] = c;
    }
    int& operator[](int index) {
        return values[index];
    }
    int operator()(int multiplier) {
        int sum = 0;
        for(int i=0; i<3; ++i) sum += values[i];
        return sum * multiplier;
    }
    operator double() const {
        double sum = 0;
        for(int i=0; i<3; ++i) sum += values[i];
        return sum / 3.0;
    }
};

int main() {
    MathBox box(2, 4, 6);
    box[1] = 10;
    int res1 = box(2);
    double res2 = box;
    cout << res1 << " " << res2;
    return 0;
}
