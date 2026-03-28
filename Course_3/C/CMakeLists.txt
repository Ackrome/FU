cmake_minimum_required(VERSION 3.10)
project(GravitySim C)

# Находим raylib
find_package(raylib CONFIG REQUIRED)

# Создаем файл
add_executable(GravitySim main.c)

# Связываем с библиотекой
target_link_libraries(GravitySim PRIVATE raylib)
