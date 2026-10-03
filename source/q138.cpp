#include <iostream>
using namespace std;
class BaseA
{
    int x, y;
public:
    BaseA(int = 1, int = 1);
    void Show();
};
BaseA::BaseA(int x, int y)
{
    this->x = x;
    this->y = y;
}
void BaseA::Show()
{
    cout << this->x * this->y;
}
class BaseB
{
    BaseA obj;
public:
    BaseB(int, int);
};
BaseB::BaseB(int x, int y) : obj(x, y)
{
    this->obj.Show();
}
int main()
{
    BaseB obj(1, 2);

    return 0;
}
