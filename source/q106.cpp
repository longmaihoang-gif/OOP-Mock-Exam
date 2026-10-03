#include <iostream>
using namespace std;
class Exam
{
    int x, y;
public:
    Exam(int = 0, int = 0);
    int GetX();
    int GetY();
};
Exam::Exam(int x, int y) : x(x), y(y)
{}
int Exam::GetX()
{
    return this->x;
}
int Exam::GetY()
{
    return this->y;
}
int main()
{
    Exam obj1;
    Exam obj2 = obj1;
    cout << obj2.GetX() << obj2.GetY();
    return 0;
}
