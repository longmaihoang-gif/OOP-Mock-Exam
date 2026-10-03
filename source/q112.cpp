#include <iostream>
using namespace std;
class Base
{
public:
    int x;
};
int main()
{
    int Base :: *ptr = &Base::x;
    Base obj;
    obj.x = 1;
    cout << obj.x;
    obj.*ptr = 2;
    cout << obj.x;

    return 0;
}
