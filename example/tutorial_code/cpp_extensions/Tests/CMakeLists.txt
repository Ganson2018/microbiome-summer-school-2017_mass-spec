
set(GTEST_INCLUDE_DIR /usr/local/include)
set(GTEST_LIBRARY_DIR /usr/local/lib)

include_directories(${GTEST_INCLUDE_DIR}) #pour touver gtest/gtest.h
link_directories(${GTEST_LIBRARY_DIR})

set(GTEST_LIBRARIES gtest gtest_main)

add_executable(heap_test heap_test.cpp)

target_link_libraries(heap_test MS pthread ${GTEST_LIBRARIES})
