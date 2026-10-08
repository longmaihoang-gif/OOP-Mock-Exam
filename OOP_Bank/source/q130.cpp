#include <iostream>
using namespace std;
class Exam
{
    int prop_x, prop_y;
public:
    ~Exam();
    void setProp();
    int Func(const Exam&);
};
Exam::~Exam()
{
}
void Exam::setProp()
{
    this->prop_x = 100;
    this->prop_y = 200;
}
int Exam::Func(const Exam& obj)
{
    return int(obj.prop_x + obj.prop_y) - 5;
}
int main()
{
    Exam obj;
    obj.setProp();
    cout << obj.Func(obj);
    return 0;
}
