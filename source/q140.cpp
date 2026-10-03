#include <iostream>
using namespace std;
class ExamB;
class ExamA
{
    int prop_x, prop_y;
public:
    int area();
    void convert(ExamB);
};
int ExamA::area()
{
    return (this->prop_x * this->prop_y);
}
void ExamA::convert(ExamB obj)
{
    this->prop_x = obj.prop_x;
    this->prop_y = obj.prop_x;
}
class ExamB
{
    int prop_x;
public:
    void setProp(int);
    friend class ExamA;
};
void ExamB::setProp(int prop_x)
{
    this->prop_x = prop_x;
}
int main()
{
    ExamB obj_b;
    ExamA obj_a;
    obj_b.setProp(6);
    obj_a.convert(obj_b);
    cout << obj_a.area();
    return 0;
}
