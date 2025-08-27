#include "sum.h"

int sum(int a, int b){
    int c = a+b;
    printk("Sum %d+%d = %d\n", a, b, c);
    return c;
}