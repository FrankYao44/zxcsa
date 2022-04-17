#include <iostream>
#include <malloc.h>
#define DEBUG
using namespace std;
void print(int i){
    #ifdef DEBUG
        cout << i << endl;
    #endif
}
void print(char c){
    #ifdef DEBUG
        cout << c << endl;
    #endif
}
void print(float f){
    #ifdef DEBUG
        cout << f << endl;
    #endif
}
void print(char* s){
    #ifdef DEBUG
        cout << s << endl;
    #endif
}
typedef struct {

} Node, *PtrToNode;

typedef struct{

} Tree;

Tree create_tree();
void insert_brother(long long data, PtrToNode p);
void insert_child(long long data, PtrToNode p);
long long pop(long long data, PtrToNode p);
PtrToNode select(long long data, Tree t);
long long find(PtrToNode p);
void update(long long data, PtrToNode p);
PtrToNode get_child(PtrToNode p);
PtrToNode get_brother(PtrToNode p);


