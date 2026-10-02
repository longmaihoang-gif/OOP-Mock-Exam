#include <iostream>
using namespace std;

void funcA(int x) {
    cout << "A:" << x << " ";
}

void funcB(int x) {
    cout << "B:" << x << " ";
}

int main() {
    void (*const pFunc)(int) = funcA;
    pFunc(5);
    
    // Thay đổi trỏ tới hàm khác
    // Chú ý pFunc là hằng con trỏ nên không thể gán lại:
    // pFunc = funcB;
    
    void (*pNormal)(int) = funcA;
    pNormal(10);
    pNormal = funcB;
    pNormal(20);
    
    return 0;
}
