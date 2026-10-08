#include <iostream>
using namespace std;
int main()
{
    int arr[] = { 0, 5, 10, 15 };
    int* ptr = arr + 2;
    int var_x = (*ptr)++;
    cout << var_x << *ptr;
    return 0;
}
