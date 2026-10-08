#include <iostream>
using namespace std;

class Score {
    int val;
public:
    explicit Score(int v) : val(v) {}
    void Print() const { cout << val; }
};

void Display(Score s) {
    s.Print();
}

int main() {
    Score s1(100);
    Display(s1);
    Display(200);
    return 0;
}
