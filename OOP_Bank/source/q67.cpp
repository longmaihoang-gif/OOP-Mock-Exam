#include <iostream>
using namespace std;

class Sample {
    int data;
public:
    Sample(int d) : data(d) {}
    friend void showData(const Sample& s);
};

void showData(const Sample& s) {
    cout << s.data;
}

int main() {
    Sample obj1(5);
    Sample obj2(10);
    showData(obj1);
    showData(obj2);
    return 0;
}
