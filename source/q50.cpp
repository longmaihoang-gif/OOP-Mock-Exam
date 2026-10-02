#include <iostream>
using namespace std;

class Demo {
private:
    int id;
    static int total;
public:
    Demo(int i) : id(i) {
        total++;
    }
    
    int getId() const {
        return id;
    }
    
    static int getTotal() {
        return total;
    }
};

int Demo::total = 0;

int main() {
    const Demo d1(100);
    Demo d2(200);
    
    cout << d1.getId() << " ";
    cout << d2.getId() << " ";
    cout << Demo::getTotal() << " ";
    
    return 0;
}
