#include <malloc.h>
#include <iostream>
typedef struct Node{
    int data;
    Node* next;
} Node;
typedef Node* PtrToNode;
typedef struct {
    PtrToNode Head;
} LNode;

LNode n;
extern "C"{
void init(){
    n.Head = (PtrToNode)malloc(sizeof(Node));
    n.Head -> data=0;
}
typedef struct {
    int list[10];
} List;
List a;
void write(int data){
    PtrToNode p = n.Head;
    while(p -> next) p = p->next;
    p -> next = (PtrToNode)malloc(sizeof(Node));
    p = p -> next;
    p -> data = data;
}

List *read(){
    int list[10] = {0};
    int i=0;
    for (PtrToNode p = n.Head; p; p = p -> next){
        a.list[i] = p->data;
        i++;

    }
    return &a;
}
//int main(){
//    init();
//    write(1);
//    write(1);
//    List pl = read();
//    for(int i=0;i<10;i++){
//        std::cout << pl.list[i] << std::endl;
//    }
//   return 0;
//}
}
