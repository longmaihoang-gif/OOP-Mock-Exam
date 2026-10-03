#include <iostream>
using namespace std;
int &Func(int var_x = 2)
{
    return var_x;
}
int main()
{
    int *ptr = &Func(5);
    cout << *ptr;
    cout << *ptr;
    return 0;
}
