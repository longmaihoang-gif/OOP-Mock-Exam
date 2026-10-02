#include <iostream>
using namespace std;

class DataManager {
private:
    int* data;
    int size;
public:
    DataManager(int s) {
        size = s;
        data = new int[size];
        for(int i=0; i<size; ++i) data[i] = i + 1;
    }
    ~DataManager() {
        delete[] data;
    }
    DataManager& operator=(const DataManager& other) {
        if (this == &other) return *this;
        delete[] data;
        size = other.size;
        data = new int[size];
        for(int i=0; i<size; ++i) {
            data[i] = other.data[i];
        }
        return *this;
    }
    void update(int idx, int val) {
        if (idx >= 0 && idx < size) data[idx] = val;
    }
    void print() const {
        for(int i=0; i<size; ++i) cout << data[i] << " ";
        cout << endl;
    }
};

int main() {
    DataManager obj1(3);
    DataManager obj2(2);
    obj2 = obj1;
    obj1.update(0, 99);
    obj2.print();
    return 0;
}
