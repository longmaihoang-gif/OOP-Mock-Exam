#include <iostream>
#include <iostream>
using namespace std;

class Resource {
public:
    Resource() { cout << "RC_DEF "; }
    Resource(int x) { cout << "RC_PAR " << x << " "; }
    Resource(const Resource& other) { cout << "RC_COPY "; }
    ~Resource() { cout << "RC_DES "; }
};

class Manager {
private:
    Resource res;
    int id;
public:
    Manager() : res(10), id(0) { cout << "M_DEF "; }
    Manager(int val) : id(val) { cout << "M_PAR "; }
    ~Manager() { cout << "M_DES "; }
};

void processTask() {
    cout << "START ";
    Manager m1;
    {
        cout << "BLOCK_IN ";
        Manager m2(5);
        cout << "BLOCK_OUT ";
    }
    cout << "END ";
}

int main() {
    cout << "MAIN_START ";
    processTask();
    cout << "MAIN_END";
    return 0;
}
