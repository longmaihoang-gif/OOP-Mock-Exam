#include <iostream>
using namespace std;
ostream& operator<<(ostream& o, int var_x)
{
    return o;
}
int main()
{
    cout << 5;

    return 0;
}
