#include <iostream>
using namespace std;
int main()
{
    int var_x = 5, var_y = 6, var_z, var_t;
    var_z = var_x, var_y;
    var_t = (var_x, var_y);
    cout << var_z << var_t;
    return 0;
}
