#include <iostream>
using namespace std;

class Configuration {
private:
    static int total_instances;
    int id;
public:
    Configuration(int id) : id(id) {
        total_instances++;
    }
    static int getTotal() {
        return total_instances;
    }
    int getId() const {
        return id;
    }
};

int Configuration::total_instances = 0;

int main() {
    Configuration c1(100);
    const Configuration c2(200);
    cout << Configuration::getTotal() << " " << c2.getId() << endl;
    return 0;
}
