#include <iostream>
using namespace std;

class Resource {
public:
    int* data;
    Resource(int val) {
        data = new int(val);
        cout << "Alloc " << *data << " ";
    }
    Resource& operator=(const Resource& other) {
        if (this == &other) return *this;
        delete data;
        data = new int(*(other.data));
        cout << "Assign " << *data << " ";
        return *this;
    }
    ~Resource() {
        if (data) {
            cout << "Del " << *data << " ";
            delete data;
        }
    }
};

int main() {
    Resource r1(5);
    Resource r2(10);
    r2 = r1;
    r1 = r1;
    return 0;
}
