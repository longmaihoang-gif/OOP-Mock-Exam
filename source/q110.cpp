#include <iostream>
using namespace std;
namespace ExamA
{
    int Func(int var_x)
    {
        cout << "A";
        return 2 * var_x;
    }
}
namespace ExamB
{
    double Func(double var_x)
    {
        cout << "B";
        return 2 * var_x;
    }
}
using namespace ExamA;
using namespace ExamB;
int main()
{
    int var_x = 10;
    double var_y = 10.0;
    cout << ExamA::Func(var_x) << ExamA::Func(var_y);
    return 0;
}
