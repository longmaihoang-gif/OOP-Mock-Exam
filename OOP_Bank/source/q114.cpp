#include <iostream>
using namespace std;
class Exam
{
public:
    int prop;
    void Func();
};
void Exam::Func()
{
    cout << "ITF";
}
void (Exam ::* pmfn)() = &Exam::Func;
int Exam ::* pmd = &Exam::prop;
int main()
{
    Exam obj;
    Exam* ptr = new Exam;
    (obj.*pmfn)();
    (ptr->*pmfn)();
    obj.*pmd = 1;
    ptr->*pmd = 2;
    cout << obj.*pmd << ptr->*pmd;
    return 0;
}
