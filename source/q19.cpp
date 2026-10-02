#include <iostream>
using namespace std;

class Resource {
private:
    int id;
public:
    Resource(int id) : id(id) {
        cout << "C" << id << " ";
    }
    ~Resource() {
        cout << "D" << id << " ";
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
    cout << "Start ";
    process();
    cout << "End";
    return 0;
}
