#include <iostream>
using namespace std;

class Widget {
private:
    int id;
    static int totalCount;
public:
    Widget(int id) : id(id) {
        totalCount++;
    }
    
    int getId() const {
        return id;
    }
    
    static void printTotal() {
        cout << totalCount;
    }
};

int Widget::totalCount = 0;

int main() {
    const Widget w1(101);
    w1.printTotal();
    return 0;
}
