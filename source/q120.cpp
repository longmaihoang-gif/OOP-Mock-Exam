#include <iostream>
using namespace std;
int main()
{
    int var_x = 5, var_y = 10, var_z = 15;
    int arr[3] = { &var_x, &var_y, &var_z };
    cout << *arr[*arr[1] - 8];
    return 0;
}
