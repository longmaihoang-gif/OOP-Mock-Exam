#include <iostream>
using namespace std;
int main()
{
    int var_x = 1;
    const int& ref_x = var_x;
    var_x++;
    cout << var_x << ref_x;
    return 0;
}
