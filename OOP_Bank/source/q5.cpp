#include <iostream>
using namespace std;

class Player {
    int score;
public:
    Player(int s) : score(s) {}
    int GetScore() { return score; }
    void SetScore(int s) { score = s; }
};

int main() {
    const Player p(100);
    cout << p.GetScore();
    return 0;
}
