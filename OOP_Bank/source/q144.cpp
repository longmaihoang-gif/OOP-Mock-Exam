#include <iostream>

using namespace std;

class Resource {
private:
    int id;
public:
    Resource(int val) : id(val) {
        cout << "C-" << id << " ";
    }
    ~Resource() {
        cout << "D-" << id << " ";
    }
};

int main() {
    Resource r1(1);
    Resource* r2 = new Resource(2);
    {
        Resource r3(3);
    }
    delete r2;
    return 0;
}
