#include <iostream>
using namespace std;

class Demo {
public:
    static void show() {
        // cout << x; // Lỗi nếu x là non-static
        cout << "Static Method";
    }
};

int main() {
    Demo::show();
    return 0;
}
