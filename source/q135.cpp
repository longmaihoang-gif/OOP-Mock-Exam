#include <iostream>
#include <string>
using namespace std;
int main()
{
    char arr[] = { "CNTT" };
    char *ptr = arr;
    ptr++;
    cout << *ptr;
    return 0;
}
