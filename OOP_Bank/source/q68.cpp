#include <iostream>
using namespace std;

class Resource {
private:
    int id;
public:
    Resource(int x) : id(x) {
        cout << "Construct " << id << endl;
    }
    ~Resource() {
        cout << "Destruct " << id << endl;
    }
};

void process() {
    Resource r1(1);
    {
        Resource r2(2);
    }
    Resource r3(3);
}

int main() {
    cout << "Start" << endl;
    process();
    cout << "End" << endl;
    return 0;
}
