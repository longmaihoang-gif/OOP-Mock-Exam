#include <iostream>
using namespace std;
class Exam
{
public:
    Exam();
    Exam(int);
    ~Exam();
};
Exam::Exam()
{
    cout << "C1";
}
Exam::Exam(int var)
{
    cout << "C2";
}
Exam::~Exam()
{
    cout << "D";
}
void Func()
{
    Exam();
    Exam(1);
}
int main()
{
    Func();
    return 0;
}
