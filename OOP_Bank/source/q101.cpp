#include <iostream>
#include <string>
using namespace std;
namespace ExamA
{
    int var_x = 10;
}
namespace ExamB
{
    int var_x = 5;
}
int main()
{
    using namespace ExamB;
    cout << ExamA::var_x;
    return 0;
}
