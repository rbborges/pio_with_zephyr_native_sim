#include <unity.h>
#include <zephyr/kernel.h>

// Declare test functions
void test_sum_positive_numbers(void);
void test_sum_negative_numbers(void);
void test_sum_zero(void);
void test_sum_large_numbers(void);

int main(void)
{
    printk("Starting Unity tests...\n");
    
    UNITY_BEGIN();
    
    RUN_TEST(test_sum_positive_numbers);
    RUN_TEST(test_sum_negative_numbers);
    RUN_TEST(test_sum_zero);
    RUN_TEST(test_sum_large_numbers);
    
    UNITY_END();
    
    return 0;
}

