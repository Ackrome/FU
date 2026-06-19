cmake_minimum_required(VERSION 3.10)

# Название проекта
project(MusicPlayer C)

# Создаем исполняемый файл из нашего исходника
add_executable(MusicPlayer main.c)

if(MSVC)
    target_compile_options(MusicPlayer PRIVATE /utf-8)
endif()

# ТА САМАЯ МАГИЯ: подключаем библиотеку Windows Multimedia для звука (winmm)
target_link_libraries(MusicPlayer winmm)

enable_testing()

add_executable(MusicPlayerTests tests/test_musicplayer.c)

if(MSVC)
    target_compile_options(MusicPlayerTests PRIVATE /utf-8)
endif()

target_link_libraries(MusicPlayerTests winmm)
add_test(NAME MusicPlayerTests COMMAND MusicPlayerTests)
