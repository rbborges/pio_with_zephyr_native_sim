#include <unity.h>
#include <zephyr/kernel.h>
#include <stdlib.h>
#include "sum.h"

void setUp(void) {
    // Set up code here, runs before each test
}

void tearDown(void) {
    // Clean up code here, runs after each test
}

void test_sum_positive_numbers(void) {
    printk("Sum 2+3 = %d\n", sum(2, 3));
    printk("Sum 4+6 = %d\n", sum(4, 6));
    printk("Sum 50+50 = %d\n", sum(50, 50));
    TEST_ASSERT_EQUAL(5, sum(2, 3));
    TEST_ASSERT_EQUAL(10, sum(4, 6));
    TEST_ASSERT_EQUAL(100, sum(50, 50));
}

void test_sum_negative_numbers(void) {
    printk("Sum -2+-3 = %d\n", sum(-2, -3));
    printk("Sum -4+3 = %d\n", sum(-4, 3));
    printk("Sum 4+-3 = %d\n", sum(4, -3));
    TEST_ASSERT_EQUAL(-5, sum(-2, -3));
    TEST_ASSERT_EQUAL(-1, sum(-4, 3));
    TEST_ASSERT_EQUAL(1, sum(4, -3));
}

void test_sum_zero(void) {
    printk("Sum 0+0 = %d\n", sum(0, 0));
    printk("Sum 5+0 = %d\n", sum(5, 0));
    printk("Sum 0+-5 = %d\n", sum(0, -5));
    TEST_ASSERT_EQUAL(0, sum(0, 0));
    TEST_ASSERT_EQUAL(5, sum(5, 0));
    TEST_ASSERT_EQUAL(-5, sum(0, -5));
}

void test_sum_large_numbers(void) {
    printk("Sum 1000000+1000000 = %d\n", sum(1000000, 1000000));
    printk("Sum 2147483647+-2147483647 = %d\n", sum(2147483647, -2147483647));
    TEST_ASSERT_EQUAL(2000000, sum(1000000, 1000000));
    TEST_ASSERT_EQUAL(0, sum(2147483647, -2147483647));
}


int main(void)
{
    printk("Starting Sum Unity tests...\n");
    
    UNITY_BEGIN();
    
    RUN_TEST(test_sum_positive_numbers);
    RUN_TEST(test_sum_negative_numbers);
    RUN_TEST(test_sum_zero);
    RUN_TEST(test_sum_large_numbers);
    
    UNITY_END();
    
    // Force exit after tests complete
    printk("Tests completed, exiting...\n");
    exit(0);
}
