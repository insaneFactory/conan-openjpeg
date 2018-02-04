cmake_minimum_required(VERSION 2.8.11)
PROJECT(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(${PROJECT_NAME} test_package.cpp)
TARGET_LINK_LIBRARIES(${PROJECT_NAME} ${CONAN_LIBS})
