cmake_minimum_required(VERSION 3.30)
project(libc C)

set(CMAKE_C_STANDARD 17)

#add_compile_options(-fPIC -Wall -O3 -march=native)
add_compile_options(-fPIC -Wall)
set(SOURCE_FILES
        main.c
        rules.c
        rules.h)

set(CMAKE_SHARED_LIBRARY_SUFFIX .so)
set(CMAKE_SHARED_LIBRARY_PREFIX)

add_executable(main main.c ${SOURCE_FILES})
add_library(libc SHARED library.c ${SOURCE_FILES})
