#include <iostream>
#include <iostream>
#include <cstring>

class MyString {
private:
    char* data;
    int size;
public:
    MyString(const char* str) {
        size = strlen(str);
        data = new char[size + 1];
        strcpy(data, str);
    }
    ~MyString() {
        delete[] data;
    }
    // [ĐIỀN CODE TẠI ĐÂY]
};

int main() {
    MyString s1("Hello");
    MyString s2 = s1;
    return 0;
}
