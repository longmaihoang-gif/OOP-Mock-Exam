#include <iostream>
using namespace std;
class Exam
{
    int prop;
    static int next_prop;
public:
    int getProp();
    Exam();
    ~Exam();
};
int Exam::next_prop = 1;
int Exam::getProp()
{
    return this->prop;
}
Exam::Exam()
{
    this->prop = Exam::next_prop++;
}
Exam::~Exam()
{
}
int main()
{
    Exam obj_x, obj_y, obj_z;
    cout << obj_x.getProp() << obj_y.getProp() << obj_z.getProp();
    return 0;
}
