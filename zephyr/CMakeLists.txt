cmake_minimum_required(VERSION 3.13.1)
# include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
message(STATUS "Hello from CMakeLists.txt!")
message(STATUS "The current source directory is: ${CMAKE_CURRENT_SOURCE_DIR}")
project(zephyr_with_native_sim)

FILE(GLOB app_sources ../src/*.c*)
target_sources(app PRIVATE ${app_sources})

# This assumes headers might be nested within lib/ subfolders.
file(GLOB_RECURSE lib_include_dirs LIST_DIRECTORIES true "../lib/*")
foreach(dir ${lib_include_dirs})
    if(IS_DIRECTORY ${dir})
        target_include_directories(app PRIVATE ${dir})
    endif()
endforeach()

file(GLOB_RECURSE app_lib_sources "../lib/*.c*")
target_sources(app PRIVATE ${app_lib_sources})