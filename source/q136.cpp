#include <iostream>
using namespace std;
int Func(int var_x, int var_y)
{
    int var_z = 0;
    while (var_y != 0)
    {
        var_z = var_z + var_x;
        var_y = var_y - 1;
    }
    return var_z;
}
int main()
{
    int var_x = 5, var_y = 5;
    cout << Func(var_x, var_y);
    return(0);
}
