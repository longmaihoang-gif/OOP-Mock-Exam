#include <iostream>
using namespace std;

class Resource {
private:
    int* data;
public:
    Resource() {
        data = new int(100);
    }
    Resource(const Resource& other) {
        data = new int(*other.data);
    }
    ~Resource() {
        delete data;
    }
};

void process(Resource r) {
    cout << "Processing" << endl;
}

int main() {
    Resource res1;
    process(res1);
    return 0;
}
