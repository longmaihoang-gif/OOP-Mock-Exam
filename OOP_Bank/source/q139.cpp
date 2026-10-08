#include <iostream>
using namespace std;
long Func(int var_x, int var_y = 5, double var_z = 5)
{
    return(++var_x * ++var_y + (int)++var_z);
}
int main()
{
    cout << Func(20, 10);
    return 0;
}
