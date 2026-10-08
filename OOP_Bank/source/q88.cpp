#include <iostream>
using namespace std;

class Engine {
public:
    Engine() { cout << "Engine_Init "; }
    ~Engine() { cout << "Engine_Destroy "; }
};

class Wheel {
public:
    Wheel() { cout << "Wheel_Init "; }
    ~Wheel() { cout << "Wheel_Destroy "; }
};

class Car {
private:
    Wheel wheel;
    Engine engine;
public:
    Car() { cout << "Car_Init "; }
    ~Car() { cout << "Car_Destroy "; }
};

int main() {
    Car myCar;
    return 0;
}
