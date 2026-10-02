#include <iostream>
#include <string>
using namespace std;

class Engine {
private:
    int horsepower;
public:
    Engine(int hp) : horsepower(hp) {
        cout << "Engine created: " << horsepower << endl;
    }
    ~Engine() {
        cout << "Engine destroyed" << endl;
    }
};

class Car {
private:
    string model;
    Engine engine;
public:
    Car(string m) : model(m), engine(300) {
        cout << "Car created: " << model << endl;
    }
    ~Car() {
        cout << "Car destroyed: " << model << endl;
    }
};

int main() {
    cout << "Start main" << endl;
    {
        Car myCar("Sedan");
    }
    cout << "End main" << endl;
    return 0;
}
