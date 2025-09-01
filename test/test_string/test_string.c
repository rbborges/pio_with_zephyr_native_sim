#include <unity.h>
#include <zephyr/kernel.h>
#include <string.h>

void setUp(void) {
    // Set up code here, runs before each test
}

void tearDown(void) {
    // Clean up code here, runs after each test
}

// Simple string operations for testing
int string_length(const char* str) {
    return strlen(str);
}

int string_compare(const char* str1, const char* str2) {
    return strcmp(str1, str2);
}

void test_string_length(void) {
    const char* test1 = "hello";
    const char* test2 = "world";
    const char* test3 = "";
    
    printk("Length of '%s' = %d\n", test1, string_length(test1));
    printk("Length of '%s' = %d\n", test2, string_length(test2));
    printk("Length of '%s' = %d\n", test3, string_length(test3));
    
    TEST_ASSERT_EQUAL(5, string_length(test1));
    TEST_ASSERT_EQUAL(5, string_length(test2));
    TEST_ASSERT_EQUAL(0, string_length(test3));
}

void test_string_compare_equal(void) {
    const char* str1 = "test";
    const char* str2 = "test";
    
    printk("Compare '%s' with '%s' = %d\n", str1, str2, string_compare(str1, str2));
    TEST_ASSERT_EQUAL(0, string_compare(str1, str2));
}

void test_string_compare_different(void) {
    const char* str1 = "abc";
    const char* str2 = "def";
    
    printk("Compare '%s' with '%s' = %d\n", str1, str2, string_compare(str1, str2));
    TEST_ASSERT_NOT_EQUAL(0, string_compare(str1, str2));
}

void test_string_empty(void) {
    const char* empty = "";
    const char* nonempty = "test";
    
    printk("Compare empty with non-empty = %d\n", string_compare(empty, nonempty));
    TEST_ASSERT_NOT_EQUAL(0, string_compare(empty, nonempty));
}

int main(void)
{
    printk("Starting String Unity tests...\n");
    
    UNITY_BEGIN();
    
    RUN_TEST(test_string_length);
    RUN_TEST(test_string_compare_equal);
    RUN_TEST(test_string_compare_different);
    RUN_TEST(test_string_empty);
    
    UNITY_END();
    
    return 0;
}

