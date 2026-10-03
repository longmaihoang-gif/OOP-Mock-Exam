#include <iostream>
using namespace std;
class Exam
{
    int var1, var2;
public:
    Exam(int = 0, int = 0);
    ~Exam();
    static void Func1();
    static void Func2();
};
Exam::Exam(int var1, int var2)
{
    this->var1 = var1;
    this->var2 = var2;
}
Exam::~Exam()
{
}
void Exam::Func1()
{
    cout << "ITF";
}
void Exam::Func2()
{
    cout << "DUT";
    this->Func1();
}
int main()
{
    Exam obj;
    obj.Func2();
    return 0;
}
