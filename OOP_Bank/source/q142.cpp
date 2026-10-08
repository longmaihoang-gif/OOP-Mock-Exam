#include <iostream>
using namespace std;
class Exam
{
public:
    Exam(char = 'C');
    ~Exam();
};
Exam::Exam(char var)
{
    cout << var;
}
Exam::~Exam()
{
    cout << 'D';
}
int main()
{
    Exam obj;
    delete obj;
    return 0;
}
