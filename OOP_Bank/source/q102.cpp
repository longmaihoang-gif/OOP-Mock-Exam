#include <iostream>
using namespace std;
int Func(int var_x, int var_y)
{
    int temp;
    while (var_y != 0)
    {
        temp = var_x % var_y;
        var_x = var_y;
        var_y = temp;
    }
    return(var_x);
}
int main()
{
    int var_x = 15, var_y = 25;
    cout << Func(var_x, var_y);
    return(0);
}
