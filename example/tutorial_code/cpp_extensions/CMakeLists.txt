cmake_minimum_required(VERSION 3.4)
project(MassSpectraAlign)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}) #for the executable
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}) #for static library
#set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}) #for shared library


add_library(MS STATIC ActiveSequence.cpp Heap.cpp)

link_directories(${PROJECT_SOURCE_DIR})

add_executable(alignment alignment.cpp)
target_link_libraries(alignment MS)

#add_subdirectory(Tests)
