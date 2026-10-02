#include <iostream>
using namespace std;

class Score {
public:
    int val;
    Score(int v = 0) : val(v) {}
    Score operator+=(const Score& other) {
        val += other.val;
        return *this;
    }
};

int main() {
    Score s1(10), s2(5), s3(2);
    (s1 += s2) += s3;
    cout << s1.val;
    return 0;
}
