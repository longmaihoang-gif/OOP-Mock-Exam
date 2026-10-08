#include <iostream>
using namespace std;
void Func(int& var_x)
{
    cout << var_x;
}
int main()
{
    float var_x = 1.23;
    Func(var_x);
    cout << var_x;
    return 0;
}
