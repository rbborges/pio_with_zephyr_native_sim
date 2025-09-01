#include <unity.h>
#include <zephyr/kernel.h>

void setUp(void) {
    // Set up code here, runs before each test
}

void tearDown(void) {
    // Clean up code here, runs after each test
}

// Simple math operations for testing
int multiply(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    if (b == 0) return 0; // Simple error handling
    return a / b;
}

void test_multiply_positive(void) {
    printk("Multiply 3*4 = %d\n", multiply(3, 4));
    printk("Multiply 5*6 = %d\n", multiply(5, 6));
    TEST_ASSERT_EQUAL(12, multiply(3, 4));
    TEST_ASSERT_EQUAL(30, multiply(5, 6));
}

void test_multiply_negative(void) {
    printk("Multiply -2*3 = %d\n", multiply(-2, 3));
    printk("Multiply -4*-5 = %d\n", multiply(-4, -5));
    TEST_ASSERT_EQUAL(-6, multiply(-2, 3));
    TEST_ASSERT_EQUAL(20, multiply(-4, -5));
}

void test_divide_positive(void) {
    printk("Divide 10/2 = %d\n", divide(10, 2));
    printk("Divide 15/3 = %d\n", divide(15, 3));
    TEST_ASSERT_EQUAL(5, divide(10, 2));
    TEST_ASSERT_EQUAL(5, divide(15, 3));
}

void test_divide_by_zero(void) {
    printk("Divide 10/0 = %d\n", divide(10, 0));
    TEST_ASSERT_EQUAL(0, divide(10, 0)); // Our simple error handling
}

int main(void)
{
    printk("Starting Math Unity tests...\n");
    
    UNITY_BEGIN();
    
    RUN_TEST(test_multiply_positive);
    RUN_TEST(test_multiply_negative);
    RUN_TEST(test_divide_positive);
    RUN_TEST(test_divide_by_zero);
    
    UNITY_END();
    
    return 0;
}

