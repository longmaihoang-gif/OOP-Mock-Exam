#include <iostream>
using namespace std;

namespace Exam
{
    int var_x;
}
void var_x()
{
    using namespace Exam;
    int var_x;
    var_x = 9;
    cout << var_x;
}
int main()
{
    enum Exam
    {
        var_x, var_y
    };
    class var_x
    {
        Exam var_y;
    };
    ::var_x();
    return 0;
}
