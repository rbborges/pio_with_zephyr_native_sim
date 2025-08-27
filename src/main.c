#include <zephyr/kernel.h>
#include "print_file_1.h"
#include "print_file_2.h"
#include "sum.h"

void main(void)
{
    printk("Hello from main!\n");
    int a = 0;
    int b = 0;

    while(true){
        print_from_file_1();
        print_from_file_2();
        sum(a, b);
        a++;
        b++;

        k_msleep(1000);
    }
}
