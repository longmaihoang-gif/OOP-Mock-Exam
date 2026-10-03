#include <iostream>
using namespace std;
class Exam
{
    static int count;
    int var;
    Exam();
    ~Exam();
};
int Exam::count;
Exam::Exam()
{
}
Exam::~Exam()
{
}
int main()
{
    cout << sizeof(Exam);
    return 0;
}
