## Введение

Язык C остается одним из базовых инструментов для изучения низкоуровневого программирования, так как он требует явного контроля памяти, аккуратной работы с указателями, буферами, строками и внешними системными API. В рамках данного проекта был разработан консольный музыкальный плеер `MusicPlayer`, реализованный в одном основном исходном файле `main.c`.

Программа предназначена для работы с локальной коллекцией MP3-файлов. Пользователь взаимодействует с приложением через текстовое меню: добавляет треки, импортирует папку, управляет воспроизведением, меняет громкость, выполняет поиск, сортировку и перемешивание плейлиста. Для демонстрации работы проекта можно использовать папку `my_songs`, расположенную рядом с исходными файлами проекта.

Проект интересен с точки зрения низкоуровневого программирования по нескольким причинам:

- данные плейлиста хранятся в двусвязном списке;
- память под каждый трек выделяется динамически через `malloc`;
- используется ручная очистка памяти через `free`;
- работа с музыкой выполняется через Windows Multimedia API;
- пути с русскими символами обрабатываются через UTF-8 и wide-строки Windows;
- реализован фоновый поток для автоматического перехода к следующему треку;
- добавлена синхронизация потоков через `CRITICAL_SECTION`;
- написаны отдельные C-тесты без внешнего тестового фреймворка.

Цель проекта - создать работоспособный консольный MP3-плеер на C, демонстрирующий работу с динамическими структурами данных, Windows API, файлами, кодировками и тестированием.

Для достижения цели были решены следующие задачи:

1. Разработать структуру данных для хранения плейлиста.
2. Реализовать добавление, удаление, сортировку, поиск и перемешивание треков.
3. Подключить воспроизведение MP3 через Windows Multimedia API.
4. Реализовать управление громкостью и отображение длительности трека.
5. Добавить автосохранение и автозагрузку плейлиста.
6. Добавить фоновый автопереход на следующий трек после окончания текущего.
7. Реализовать проверку существования файлов перед добавлением и загрузкой.
8. Написать тесты для ключевой логики проекта.

## Постановка задачи

Необходимо разработать консольное приложение на языке C для управления локальным музыкальным плейлистом и воспроизведения MP3-файлов в операционной системе Windows.

Приложение должно позволять пользователю:

- добавлять отдельные MP3-файлы;
- импортировать все MP3-файлы из указанной папки;
- просматривать текущий плейлист;
- запускать, останавливать и ставить воспроизведение на паузу;
- переходить к следующему и предыдущему треку;
- удалять треки из списка;
- сортировать плейлист по названию;
- искать треки по части названия или имени исполнителя;
- перемешивать порядок треков;
- изменять громкость через команды `+` и `-`;
- сохранять плейлист и загружать его повторно;
- автоматически переходить на следующий трек после завершения текущего.

При этом программа должна корректно работать с русскими именами файлов, не терять данные при выходе и освобождать выделенную динамическую память.

## Критерии готовности проекта

Проект считается завершенным, если выполняются следующие условия:

1. Программа собирается через CMake и запускается в Windows-консоли.
2. Плейлист хранится в динамической структуре данных, а не в статическом массиве.
3. Пользователь может выполнить все основные операции через меню.
4. Воспроизведение MP3 работает через Windows Multimedia API.
5. Громкость изменяется без перезапуска программы.
6. При запуске трека отображается его длительность в формате `мм:сс`.
7. Плейлист и настройки сохраняются между запусками.
8. Проверка файлов предотвращает добавление несуществующих путей.
9. Тесты проверяют ключевые функции без ручного запуска интерактивного меню.
10. Пользовательская документация и отчет описывают основные возможности проекта.

## 1. Описание предметной области и логики приложения

Проект относится к области локальных медиаплееров. В отличие от полноценных графических аудиоплееров, здесь интерфейс остается консольным, а акцент сделан на внутренней логике: хранении списка треков, навигации по нему и управлении воспроизведением.

Пользователь работает с программой через главное меню. Перед каждым вводом команды экран очищается через `system("cls")`, после чего сверху выводится статус операции, ниже - панель результатов, а затем само меню. Такой подход делает консольный интерфейс более стабильным визуально: сообщения не накапливаются бесконечной лентой, а меню остается на одном и том же месте.

Рис. 1 показывает стартовый экран приложения.

![Рис. 1. Главное меню MusicPlayer](docs/assets/screen_main_menu.png)

Основной сценарий работы выглядит так:

1. Пользователь запускает программу.
2. Программа пытается загрузить `playlist.txt` и `settings.txt`.
3. Если плейлист отсутствует, пользователь импортирует папку `my_songs` или добавляет треки вручную.
4. Пользователь запускает воспроизведение.
5. Программа открывает текущий MP3-файл через MCI, применяет громкость и выводит длительность.
6. После окончания трека фоновый поток автоматически включает следующий.
7. При выходе программа сохраняет плейлист и настройки.

Для демонстрации в проекте используется папка `my_songs`, содержащая следующие MP3-файлы:

- `Junkyard Sunny - Vasco.mp3`;
- `kahoot! - Hirs Heres.mp3`;
- `Запретил - Роскомнадзор.mp3`;
- `Темная ночь - Марк Бернес.mp3`;
- `Тип-топ - Микки Маус.mp3`.

Рис. 2 показывает процесс загрузки песен из относительного пути `my_songs`.

![Рис. 2. Импорт папки my_songs](docs/assets/screen_import_folder.png)

После импорта треки попадают в двусвязный список и могут быть отображены через команду `6`.

![Рис. 3. Вывод плейлиста после импорта my_songs](docs/assets/screen_playlist.png)

## 2. Архитектура программного решения

Проект состоит из нескольких основных частей:

- `main.c` - основной исходный файл с логикой плеера;
- `CMakeLists.txt` - сборочный файл CMake;
- `.vscode/tasks.json` - задача сборки для Visual Studio Code;
- `tests/test_musicplayer.c` - набор тестов;
- `wiki.md` - пользовательская документация;
- `project_report.md` - данный отчет;
- `my_songs` - демонстрационная папка с MP3;
- `playlist.txt` - файл плейлиста, создается программой;
- `settings.txt` - файл настроек, создается программой.

Общая архитектура показана на рис. 4.

![Рис. 4. Архитектура проекта](docs/assets/diagram_architecture.png)

В центре архитектуры находится `main.c`. Именно этот файл связывает между собой:

- консольное меню;
- структуру плейлиста;
- работу с файлами;
- Windows Multimedia API;
- систему тестирования.

Программа не разделена на отдельные `.h` и `.c` модули, однако внутри `main.c` логика разбита на группы функций:

- служебные функции строк и статуса;
- функции кодировки и проверки файлов;
- функции плейлиста;
- функции воспроизведения;
- функции сохранения и загрузки;
- функции поиска, сортировки и перемешивания;
- функции фонового потока;
- функции интерфейса.

Такое разделение внутри одного файла делает код достаточно понятным для учебного проекта и одновременно позволяет тестировать отдельные части программы.

## 3. Структуры данных

### 3.1. Структура `Track`

Для хранения одного трека используется структура `Track`.

![Рис. 5. Код структур Track и Playlist](docs/assets/code_structs.png)

Поля структуры:

- `title` - название трека;
- `artist` - исполнитель;
- `filepath` - путь к MP3-файлу;
- `next` - указатель на следующий элемент списка;
- `prev` - указатель на предыдущий элемент списка.

Размеры строковых буферов заданы через макросы:

- `TITLE_SIZE = 100`;
- `ARTIST_SIZE = 100`;
- `PATH_SIZE = 512`.

Такой подход упрощает контроль размеров и позволяет менять лимиты централизованно.

### 3.2. Структура `Playlist`

Плейлист представлен структурой `Playlist`.

Она содержит:

- `head` - указатель на первый трек;
- `tail` - указатель на последний трек;
- `current` - указатель на текущий трек;
- `size` - количество треков.

Использование `head` и `tail` позволяет быстро обращаться к началу и концу списка. Это важно для закольцовки:

- если пользователь нажал «следующий» на последнем треке, программа переходит к `head`;
- если пользователь нажал «предыдущий» на первом треке, программа переходит к `tail`.

Схема двусвязного списка приведена на рис. 6.

![Рис. 6. Двусвязный список плейлиста](docs/assets/diagram_playlist.png)

### 3.3. Почему выбран двусвязный список

Двусвязный список хорошо подходит для данного проекта, потому что:

- можно переходить вперед и назад;
- можно удалить текущий элемент без полного пересоздания массива;
- можно хранить указатель на текущий трек;
- можно перемешивать список, переставляя связи между узлами;
- структура наглядно демонстрирует работу с указателями.

Недостатки такого подхода:

- для поиска элемента по номеру нужно пройти список от начала;
- сортировка и shuffle требуют аккуратного обновления `prev` и `next`;
- ошибки в указателях могут привести к повреждению списка.

## 4. Главное меню и пользовательский интерфейс

Меню реализовано функциями:

- `print_menu`;
- `render_screen`.

`render_screen` очищает экран, печатает статус, панель результатов и меню. Благодаря этому пользователь всегда видит актуальное состояние программы сверху.

Команды меню:

| Команда | Назначение |
|---|---|
| `1` | Играть текущий трек |
| `2` | Пауза или продолжение |
| `3` | Стоп |
| `4` | Следующий трек |
| `5` | Предыдущий трек |
| `6` | Показать плейлист |
| `7` | Добавить трек или импортировать папку |
| `8` | Удалить трек |
| `9` | Отсортировать по алфавиту |
| `10` | Сохранить или загрузить плейлист |
| `11` | Поиск |
| `12` | Shuffle |
| `+` | Увеличить громкость |
| `-` | Уменьшить громкость |
| `0` | Выход |

Ввод команды хранится не как число, а как строка:

```text
scanf("%15s", choice)
```

Это нужно, потому что меню принимает не только числовые команды, но и символы `+` и `-`.

## 5. Работа с плейлистом

### 5.1. Инициализация

Функция `init_playlist` устанавливает все указатели в `NULL`, а размер списка в `0`.

После инициализации плейлист считается пустым:

- `head = NULL`;
- `tail = NULL`;
- `current = NULL`;
- `size = 0`.

### 5.2. Создание трека

Функция `create_track` выделяет память через `malloc`, копирует название, исполнителя и путь, затем инициализирует `next` и `prev`.

Если память выделить не удалось, функция возвращает `NULL` и пишет сообщение в статус.

Для копирования строк используется helper `copy_string`, который внутри применяет `snprintf`. Это безопаснее, чем прямой `strcpy`, потому что учитывает размер буфера.

### 5.3. Добавление в конец

Функция `add_track_end` добавляет новый трек в конец списка.

Если список пуст:

- `head` указывает на новый трек;
- `tail` указывает на новый трек;
- `current` тоже указывает на новый трек.

Если список не пуст:

- старый `tail->next` указывает на новый трек;
- `new_track->prev` указывает на старый `tail`;
- `tail` обновляется.

### 5.4. Удаление по номеру

Функция `remove_track_by_index` удаляет трек по номеру.

Алгоритм:

1. Проверить корректность номера.
2. Пройти список до нужного элемента.
3. Если удаляемый трек является текущим, остановить музыку.
4. Перевязать соседние узлы.
5. Обновить `head` или `tail`, если удаляется первый или последний элемент.
6. Освободить память через `free`.
7. Уменьшить `size`.

### 5.5. Очистка

Функция `clear_playlist` проходит по списку от `head` до конца и освобождает каждый узел.

После очистки:

- `head = NULL`;
- `tail = NULL`;
- `current = NULL`;
- `size = 0`.

Это нужно при выходе из программы и при загрузке нового плейлиста из файла.

## 6. Импорт треков

### 6.1. Ручное добавление

Ручное добавление выполняется через команду `7`, затем подкоманду `1`.

Пользователь вводит:

1. Исполнителя.
2. Название.
3. Полный путь к MP3.

Перед добавлением выполняются проверки:

- исполнитель не пустой;
- название не пустое;
- путь не пустой;
- расширение равно `.mp3`;
- файл существует;
- путь указывает именно на файл, а не папку.

Если путь заключен в кавычки, они удаляются функцией `strip_surrounding_quotes`.

### 6.2. Импорт папки

Импорт папки выполняется через команду `7`, затем подкоманду `2`.

Пользователь вводит путь к папке. Для демонстрации можно использовать:

```text
my_songs
```

Программа строит маску поиска:

```text
my_songs\*.*
```

Затем через Windows API `FindFirstFileW` и `FindNextFileW` проходит по файлам папки. В список добавляются только файлы с расширением `.mp3`.

Для каждого MP3:

- если ID3v1-теги найдены, используются исполнитель и название из тегов;
- если тегов нет, название берется из имени файла без расширения;
- исполнитель устанавливается как `Unknown`.

Импорт не является рекурсивным: подпапки не обходятся.

## 7. Воспроизведение через Windows Multimedia API

Воспроизведение реализовано через MCI. Это старый, но удобный интерфейс Windows для простого управления мультимедиа из C.

Программа использует alias:

```text
track
```

### 7.1. Открытие файла

Для открытия MP3 формируется команда:

```text
open "<путь>" type mpegvideo alias track
```

Так как путь может содержать русские символы, команда переводится из UTF-8 в wide-строку и отправляется через `mciSendStringW`.

### 7.2. Запуск

После успешного открытия вызывается:

```text
play track
```

### 7.3. Пауза

Команда паузы:

```text
pause track
```

### 7.4. Продолжение

Команда продолжения:

```text
resume track
```

### 7.5. Остановка

Функция `stop_music` отправляет две команды:

```text
stop track
close track
```

После этого сбрасываются флаги:

- `g_track_open = 0`;
- `g_is_paused = 0`;
- `g_last_track_start_tick = 0`.

### 7.6. Длительность трека

Перед получением длительности программа устанавливает формат времени:

```text
set track time format milliseconds
```

Затем получает длину:

```text
status track length
```

Ответ приходит в миллисекундах. Функция `format_duration` переводит это значение в формат `мм:сс`.

Пример:

```text
[▶] Играет: Unknown - Темная ночь - Марк Бернес (03:15)
```

Если длину получить не удалось, выводится:

```text
--:--
```

## 8. Управление громкостью

Громкость хранится в переменной `g_volume`.

Диапазон:

- `0` - 0%;
- `1000` - 100%.

Шаг:

- `100`, то есть 10%.

Команда `+` увеличивает громкость, команда `-` уменьшает.

Перед сохранением значение проходит через `clamp_volume`, чтобы не выйти за пределы `0..1000`.

Если трек открыт, громкость сразу применяется командой:

```text
setaudio track volume to <значение>
```

После изменения громкости вызывается `save_settings`, поэтому новое значение сразу записывается в `settings.txt`.

## 9. Поиск

Поиск запускается командой `11`.

Пользователь вводит слово, после чего программа проходит по всем трекам и проверяет:

- есть ли слово в названии;
- есть ли слово в исполнителе.

Пример поиска по слову `ночь` показан на рис. 7.

![Рис. 7. Поиск по слову "ночь"](docs/assets/screen_search.png)

Поиск выполняется без учета регистра. Это значит, что запросы:

- `ночь`;
- `Ночь`;
- `НОЧЬ`;

будут считаться совпадающими.

Ключевой фрагмент реализации приведен на рис. 8.

![Рис. 8. Код регистронезависимого поиска](docs/assets/code_search.png)

Технически поиск работает так:

1. UTF-8 строка переводится в wide-строку Windows.
2. По строке выполняется проход окном длиной запроса.
3. Для каждого окна вызывается `CompareStringOrdinal` с флагом `TRUE`.
4. Если сравнение вернуло `CSTR_EQUAL`, совпадение найдено.

Если преобразование UTF-8 в wide-строку не удалось, используется fallback через `strstr`.

## 10. Сортировка

Сортировка выполняется командой `9`.

В проекте реализована сортировка двусвязного списка по названию трека. Важно, что сортировка переставляет сами узлы списка, а не просто меняет данные внутри структур.

Это решение лучше, потому что:

- указатель `current` остается указывать на тот же объект `Track`;
- текущий трек не «подменяется» другим после сортировки;
- логика списка остается корректной.

Алгоритм работает как вставка узлов в новый отсортированный список:

1. Берется очередной узел исходного списка.
2. У него временно сбрасываются `prev` и `next`.
3. Узел вставляется в правильное место нового списка.
4. После обработки всех узлов обновляются `head` и `tail`.

## 11. Shuffle

Shuffle запускается командой `12`.

Алгоритм:

1. Все указатели на узлы списка копируются во временный массив.
2. Массив перемешивается алгоритмом Fisher-Yates.
3. Узлы связываются заново через `prev` и `next`.
4. Обновляются `head` и `tail`.

Особенность: текущий трек остается тем же указателем. Меняется только позиция узла в списке.

Это важно, потому что пользователь может перемешать плейлист во время работы, не потеряв выбранный текущий трек.

## 12. Сохранение и загрузка

### 12.1. Сохранение плейлиста

Функция `save_playlist` записывает каждый трек в файл:

```text
Исполнитель|Название|Путь
```

Файл по умолчанию:

```text
playlist.txt
```

### 12.2. Загрузка плейлиста

Функция `load_playlist` читает `playlist.txt`, разбивает строки через `strtok` и добавляет доступные файлы в список.

Перед загрузкой:

- музыка останавливается;
- текущий плейлист очищается.

При загрузке программа проверяет существование файла. Если файл недоступен, он пропускается. В статусе выводится количество загруженных и пропущенных треков.

### 12.3. Настройки

Файл:

```text
settings.txt
```

Содержит текущую громкость:

```text
volume=900
```

При запуске вызывается `load_settings`, при выходе и изменении громкости - `save_settings`.

## 13. Автопереход на следующий трек

Автопереход реализован фоновым потоком Windows.

Функции:

- `start_auto_next_monitor`;
- `auto_next_monitor`;
- `stop_auto_next_monitor`.

После запуска трека программа сохраняет время старта в `g_last_track_start_tick`.

Фоновый поток раз в `AUTO_NEXT_POLL_MS` миллисекунд проверяет состояние MCI:

```text
status track mode
```

Если состояние равно:

```text
stopped
```

и трек не находится на паузе, вызывается `play_next`.

Чтобы MCI не был ошибочно воспринят как остановленный сразу после запуска, используется задержка:

```text
AUTO_NEXT_START_GRACE_MS = 1500
```

## 14. Синхронизация потоков

Так как главный поток обрабатывает меню, а фоновый поток может включить следующий трек, доступ к состоянию плеера защищен критической секцией.

Глобальные переменные:

- `g_player_lock`;
- `g_player_lock_ready`.

Функции-обертки:

- `lock_player`;
- `unlock_player`.

Критическая секция защищает:

- переключение треков;
- работу с MCI;
- загрузку и сохранение плейлиста;
- очистку списка;
- вывод экрана;
- изменение глобального состояния.

## 15. Кодировки

Проект использует UTF-8 для строк в исходном коде и консоли.

В `main` вызываются:

```text
SetConsoleOutputCP(CP_UTF8)
SetConsoleCP(CP_UTF8)
```

Для MSVC включен флаг:

```text
/utf-8
```

Пути к файлам переводятся в wide-строки через `MultiByteToWideChar`. Это нужно, чтобы Windows API мог корректно открывать файлы с русскими символами в имени.

Пример файлов из `my_songs`:

- `Запретил - Роскомнадзор.mp3`;
- `Темная ночь - Марк Бернес.mp3`;
- `Тип-топ - Микки Маус.mp3`.

## 16. Чтение ID3v1

Функция `get_id3v1_tags` пытается прочитать ID3v1-теги из MP3.

ID3v1 находится в последних 128 байтах файла.

Проверяется метка:

```text
TAG
```

Затем читаются:

- 30 байт названия;
- 30 байт исполнителя.

Пробелы справа удаляются функцией `trim_trailing_spaces`.

Так как русские ID3v1-теги часто записаны в Windows-1251, программа:

1. Переводит байты из Windows-1251 в wide-строку.
2. Затем переводит wide-строку в UTF-8.

Если теги отсутствуют или пустые, при импорте папки используется имя файла.

## 17. Тестирование

Для проекта написаны тесты в файле:

```text
tests/test_musicplayer.c
```

Тесты подключают `main.c` напрямую:

```text
#define MUSICPLAYER_TEST
#include "../main.c"
```

Для этого интерактивная функция `main` в `main.c` обернута в:

```text
#ifndef MUSICPLAYER_TEST
...
#endif
```

Так тесты могут обращаться к внутренним функциям без запуска меню.

Тесты проверяют:

- удаление кавычек из путей;
- безопасное копирование строк;
- форматирование длительности;
- ограничение громкости;
- изменение громкости;
- добавление треков;
- удаление треков;
- очистку списка;
- сортировку;
- сохранение текущего узла после сортировки;
- Shuffle;
- поиск без учета регистра;
- поиск по русскому тексту;
- проверку существования файла;
- сохранение и загрузку плейлиста;
- пропуск отсутствующих файлов;
- сохранение и загрузку настроек.

Результат тестового запуска показан на рис. 9.

![Рис. 9. Результат запуска тестов](docs/assets/screen_tests.png)

Тесты можно собрать через CMake:

```text
cmake --build build --target MusicPlayerTests
ctest --test-dir build --output-on-failure
```

Либо напрямую через MSVC Developer Command Prompt:

```text
cl.exe /nologo /W4 /utf-8 /TC /Fe:build\test_musicplayer.exe tests\test_musicplayer.c /link winmm.lib
build\test_musicplayer.exe
```

## 18. Безопасность и надежность

В проекте используются следующие меры защиты:

- проверка результата `malloc`;
- ограниченное копирование строк через `snprintf`;
- проверка длины команд перед передачей MCI;
- проверка существования файла перед добавлением;
- пропуск недоступных файлов при загрузке;
- закрытие MCI-устройства при остановке;
- очистка памяти при выходе;
- критическая секция для синхронизации потоков;
- тесты на основные операции со списком.

Оставшиеся риски:

- текстовый формат плейлиста не экранирует символ `|`;
- фиксированные буферы могут обрезать очень длинные названия;
- MCI может не воспроизвести некоторые MP3-кодеки;
- фоновый поток проверяет окончание трека с задержкой до 1 секунды;
- ID3v2 не поддерживается.

## 19. Технические особенности

Ключевые технические решения проекта:

- двусвязный список вместо массива;
- ручная работа с памятью;
- Windows MCI вместо сторонней библиотеки;
- UTF-8 в исходниках и консоли;
- wide-вызовы Windows API для путей;
- фоновый поток для автоперехода;
- сохранение настроек в простом текстовом файле;
- тестовый harness без сторонних зависимостей.

Такой набор решений хорошо подходит для учебного проекта по низкоуровневому программированию, потому что демонстрирует сразу несколько важных тем языка C:

- указатели;
- структуры;
- динамическая память;
- файлы;
- строки;
- системные вызовы;
- потоки;
- синхронизация;
- тестирование.

## Заключение

В результате работы был создан консольный MP3-плеер `MusicPlayer` на языке C. Программа умеет управлять плейлистом, воспроизводить локальные MP3-файлы, работать с русскими путями, управлять громкостью, искать треки, сортировать и перемешивать список.

Основная структура данных проекта - двусвязный список. Она позволяет двигаться по плейлисту вперед и назад, удалять элементы и сохранять текущий трек при сортировке и перемешивании.

Для воспроизведения используется Windows Multimedia API, что делает проект зависимым от Windows, но позволяет обойтись без внешних аудиобиблиотек. Работа с русскими символами обеспечивается через UTF-8, `MultiByteToWideChar` и wide-функции Windows API.

Дополнительно реализованы автосохранение, автозагрузка, проверка файлов, фоновый автопереход и отдельный набор тестов. Тестирование подтвердило корректность ключевых частей логики: список, сортировка, shuffle, поиск, файлы и настройки.

Проект можно развивать дальше: добавить ID3v2, рекурсивный импорт папок, прогресс воспроизведения, горячие клавиши без Enter и более надежный формат хранения плейлиста.

## Список источников

1. Документация Microsoft по Windows Multimedia API и MCI.
2. Документация Microsoft по функциям работы с файлами WinAPI.
3. Документация Microsoft по `CRITICAL_SECTION` и `CreateThread`.
4. Стандартная библиотека C: `stdio.h`, `stdlib.h`, `string.h`, `time.h`, `wchar.h`.
5. Исходный код проекта: `main.c`, `tests/test_musicplayer.c`, `CMakeLists.txt`.

## Приложение

### Использованные демонстрационные треки

Файлы из папки `my_songs`:

- `Junkyard Sunny - Vasco.mp3`;
- `kahoot! - Hirs Heres.mp3`;
- `Запретил - Роскомнадзор.mp3`;
- `Темная ночь - Марк Бернес.mp3`;
- `Тип-топ - Микки Маус.mp3`.

### Сгенерированные изображения

Все изображения для отчета находятся в папке:

```text
docs/assets
```

Список изображений:

- `screen_main_menu.png`;
- `screen_import_folder.png`;
- `screen_playlist.png`;
- `screen_search.png`;
- `screen_tests.png`;
- `diagram_architecture.png`;
- `diagram_playlist.png`;
- `code_structs.png`;
- `code_search.png`.

Схемы выполнены на белом фоне. Скриншоты кода выполнены на черном фоне.

### Полный листинг `main.c`

Ниже приведено полное содержимое файла `main.c` на момент подготовки отчета.

```c
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>
#include <wchar.h>
#include <windows.h> // Для работы со звуком и кодировками
#include <mmsystem.h>

#define TITLE_SIZE 100
#define ARTIST_SIZE 100
#define PATH_SIZE 512
#define COMMAND_SIZE 1024
#define PLAYLIST_LINE_SIZE (TITLE_SIZE + ARTIST_SIZE + PATH_SIZE + 4)
#define DURATION_TEXT_SIZE 16
#define MENU_INPUT_SIZE 16
#define STATUS_MESSAGE_SIZE 512
#define PANEL_TEXT_SIZE 8192
#define WIDE_TEXT_SIZE 512
#define DEFAULT_PLAYLIST_FILE "playlist.txt"
#define SETTINGS_FILE "settings.txt"
#define AUTO_NEXT_POLL_MS 1000
#define AUTO_NEXT_START_GRACE_MS 1500
#define VOLUME_MIN 0
#define VOLUME_MAX 1000
#define VOLUME_STEP 100

// --- СТРУКТУРЫ ДАННЫХ ---
typedef struct Track {
    char title[TITLE_SIZE];
    char artist[ARTIST_SIZE];
    char filepath[PATH_SIZE];
    
    struct Track* next;
    struct Track* prev;
} Track;

typedef struct Playlist {
    Track* head;
    Track* tail;
    Track* current;
    int size;
} Playlist;

static int g_track_open = 0;
static int g_is_paused = 0;
static int g_volume = VOLUME_MAX;
static char g_status_message[STATUS_MESSAGE_SIZE] = "Готово.";
static char g_panel_text[PANEL_TEXT_SIZE] = "";
static CRITICAL_SECTION g_player_lock;
static int g_player_lock_ready = 0;
static HANDLE g_auto_next_thread = NULL;
static volatile LONG g_auto_next_running = 0;
static DWORD g_last_track_start_tick = 0;

int get_id3v1_tags(const char* filepath, char* out_title, char* out_artist);
void play_next(Playlist* pl);
void clear_playlist(Playlist* pl);
static int clamp_volume(int volume);

static void copy_string(char* destination, size_t destination_size, const char* source) {
    if (destination_size == 0) return;

    if (source == NULL) {
        destination[0] = '\0';
        return;
    }

    snprintf(destination, destination_size, "%s", source);
}

static void strip_surrounding_quotes(char* value) {
    size_t len = strlen(value);

    if (len >= 2 && value[0] == '"' && value[len - 1] == '"') {
        memmove(value, value + 1, len - 2);
        value[len - 2] = '\0';
    } else if (len > 0 && value[0] == '"') {
        memmove(value, value + 1, len);
    }
}

static void set_status(const char* format, ...) {
    va_list args;
    va_start(args, format);
    vsnprintf(g_status_message, sizeof(g_status_message), format, args);
    va_end(args);
}

static void clear_panel(void) {
    g_panel_text[0] = '\0';
}

static void append_panel(const char* format, ...) {
    size_t used = strlen(g_panel_text);
    size_t remaining = sizeof(g_panel_text) - used;
    va_list args;

    if (remaining <= 1) return;

    va_start(args, format);
    vsnprintf(g_panel_text + used, remaining, format, args);
    va_end(args);
}

static void lock_player(void) {
    if (g_player_lock_ready) {
        EnterCriticalSection(&g_player_lock);
    }
}

static void unlock_player(void) {
    if (g_player_lock_ready) {
        LeaveCriticalSection(&g_player_lock);
    }
}

static int utf8_to_wide(const char* source, wchar_t* destination, int destination_size) {
    if (source == NULL || destination == NULL || destination_size <= 0) return 0;
    return MultiByteToWideChar(CP_UTF8, 0, source, -1, destination, destination_size) != 0;
}

static int file_exists_utf8(const char* filepath) {
    wchar_t wfilepath[PATH_SIZE];
    DWORD attributes;

    if (!utf8_to_wide(filepath, wfilepath, PATH_SIZE)) {
        return 0;
    }

    attributes = GetFileAttributesW(wfilepath);
    return attributes != INVALID_FILE_ATTRIBUTES && !(attributes & FILE_ATTRIBUTE_DIRECTORY);
}

static int contains_ignore_case_utf8(const char* text, const char* query) {
    wchar_t wtext[WIDE_TEXT_SIZE];
    wchar_t wquery[WIDE_TEXT_SIZE];
    size_t text_len;
    size_t query_len;

    if (text == NULL || query == NULL || query[0] == '\0') return 0;

    if (!utf8_to_wide(text, wtext, WIDE_TEXT_SIZE) ||
        !utf8_to_wide(query, wquery, WIDE_TEXT_SIZE)) {
        return strstr(text, query) != NULL;
    }

    text_len = wcslen(wtext);
    query_len = wcslen(wquery);
    if (text_len == 0 || query_len == 0) return 0;

    if (query_len > text_len) return 0;

    for (size_t i = 0; i <= text_len - query_len; i++) {
        if (CompareStringOrdinal(wtext + i, (int)query_len, wquery, (int)query_len, TRUE) == CSTR_EQUAL) {
            return 1;
        }
    }

    return 0;
}

static void save_settings(void) {
    FILE* file = fopen(SETTINGS_FILE, "w");
    if (file == NULL) return;

    fprintf(file, "volume=%d\n", g_volume);
    fclose(file);
}

static void load_settings(void) {
    FILE* file = fopen(SETTINGS_FILE, "r");
    char line[64];
    int volume;

    if (file == NULL) return;

    while (fgets(line, sizeof(line), file)) {
        if (sscanf(line, "volume=%d", &volume) == 1) {
            g_volume = clamp_volume(volume);
        }
    }

    fclose(file);
}

static void print_mci_error(const char* message, MCIERROR err) {
    wchar_t werror[256];
    char error_text[512];

    if (mciGetErrorStringW(err, werror, 256) &&
        WideCharToMultiByte(CP_UTF8, 0, werror, -1, error_text, sizeof(error_text), NULL, NULL) != 0) {
        set_status("[!] %s: %s", message, error_text);
    } else {
        set_status("[!] %s. Код ошибки MCI: %lu", message, (unsigned long)err);
    }
}

static int clamp_volume(int volume) {
    if (volume < VOLUME_MIN) return VOLUME_MIN;
    if (volume > VOLUME_MAX) return VOLUME_MAX;
    return volume;
}

static MCIERROR apply_volume_to_open_track(void) {
    char command[64];
    snprintf(command, sizeof(command), "setaudio track volume to %d", g_volume);
    return mciSendStringA(command, NULL, 0, NULL);
}

static void print_volume(void) {
    clear_panel();
    set_status("[VOLUME] Громкость: %d%%", g_volume / 10);
}

static void change_volume(int delta) {
    int old_volume = g_volume;
    clear_panel();
    g_volume = clamp_volume(g_volume + delta);

    if (g_track_open) {
        MCIERROR err = apply_volume_to_open_track();
        if (err != 0) {
            g_volume = old_volume;
            print_mci_error("Ошибка изменения громкости", err);
            return;
        }
    }

    print_volume();
    save_settings();
}

static void increase_volume(void) {
    change_volume(VOLUME_STEP);
}

static void decrease_volume(void) {
    change_volume(-VOLUME_STEP);
}

static int get_current_track_duration_ms(long* duration_ms) {
    char duration_text[64];
    char* end = NULL;
    MCIERROR err;

    if (duration_ms == NULL) return 0;

    err = mciSendStringA("set track time format milliseconds", NULL, 0, NULL);
    if (err != 0) return 0;

    duration_text[0] = '\0';
    err = mciSendStringA("status track length", duration_text, sizeof(duration_text), NULL);
    if (err != 0) return 0;

    *duration_ms = strtol(duration_text, &end, 10);
    return end != duration_text && *duration_ms >= 0;
}

static void format_duration(long duration_ms, char* output, size_t output_size) {
    long total_seconds;
    long minutes;
    long seconds;

    if (output_size == 0) return;

    if (duration_ms < 0) {
        snprintf(output, output_size, "--:--");
        return;
    }

    total_seconds = duration_ms / 1000;
    minutes = total_seconds / 60;
    seconds = total_seconds % 60;
    snprintf(output, output_size, "%02ld:%02ld", minutes, seconds);
}

// --- СИСТЕМНЫЕ ФУНКЦИИ СПИСКА (Блок 1) ---

// 1. Инициализация пустого плейлиста
void init_playlist(Playlist* pl) {
    pl->head = NULL;
    pl->tail = NULL;
    pl->current = NULL;
    pl->size = 0;
}

// 2. Создание нового узла
Track* create_track(const char* title, const char* artist, const char* filepath) {
    Track* new_track = (Track*)malloc(sizeof(*new_track));
    if (new_track == NULL) {
        set_status("[!] Ошибка: не удалось выделить память для трека.");
        return NULL;
    }

    copy_string(new_track->title, sizeof(new_track->title), title);
    copy_string(new_track->artist, sizeof(new_track->artist), artist);
    copy_string(new_track->filepath, sizeof(new_track->filepath), filepath);
    new_track->next = NULL;
    new_track->prev = NULL;
    return new_track;
}

// 3. Добавление трека в конец списка
void add_track_end(Playlist* pl, const char* title, const char* artist, const char* filepath) {
    Track* new_track = create_track(title, artist, filepath);
    if (new_track == NULL) return;
    
    if (pl->head == NULL) {
        pl->head = new_track;
        pl->tail = new_track;
        pl->current = new_track; // Если это первый трек, он становится текущим
    } else {
        pl->tail->next = new_track;
        new_track->prev = pl->tail;
        pl->tail = new_track;
    }
    pl->size++;
}

// --- ФУНКЦИИ ПЛЕЕРА (Блок 2) ---

// 4. Остановка музыки
void stop_music() {
    // Останавливаем и закрываем конкретный поток track
    mciSendStringA("stop track", NULL, 0, NULL);
    mciSendStringA("close track", NULL, 0, NULL);
    g_track_open = 0;
    g_is_paused = 0;
    g_last_track_start_tick = 0;
}

// 5. Воспроизведение текущего трека (с поддержкой русских букв!)
void play_current(Playlist* pl) {
    clear_panel();

    if (pl->current == NULL) {
        set_status("[!] Плейлист пуст.");
        return;
    }
    
    char command[COMMAND_SIZE];
    char duration_text[DURATION_TEXT_SIZE] = "--:--";
    long duration_ms;
    
    const char* ext = strrchr(pl->current->filepath, '.');
    // Если это НЕ mp3, выводим красивое сообщение и выходим из функции
    if (ext == NULL || _stricmp(ext, ".mp3") != 0) {
        set_status("[!] Трек '%s' пропущен. Windows MCI поддерживает здесь только .mp3. Нажмите '4' для следующего.", pl->current->title);
        return;
    }

    if (!file_exists_utf8(pl->current->filepath)) {
        set_status("[!] Файл трека не найден: %s", pl->current->filepath);
        return;
    }

    stop_music(); // Сначала останавливаем предыдущий трек

    // Для MP3 жестко указываем тип mpegvideo
    int written = snprintf(command, sizeof(command), "open \"%s\" type mpegvideo alias track", pl->current->filepath);
    if (written < 0 || written >= (int)sizeof(command)) {
        set_status("[!] Ошибка: путь к файлу слишком длинный.");
        return;
    }
    
    // --- МАГИЯ WINDOWS: ПЕРЕВОДИМ UTF-8 в UNICODE ---
    wchar_t wcommand[COMMAND_SIZE]; // "Широкая" строка
    if (MultiByteToWideChar(CP_UTF8, 0, command, -1, wcommand, COMMAND_SIZE) == 0) {
        set_status("[!] Ошибка преобразования пути в Unicode.");
        return;
    }
    
    // Вызываем функцию с буквой W (Wide), передавая ей Unicode-строку
    MCIERROR err = mciSendStringW(wcommand, NULL, 0, NULL);
    
    if (err != 0) {
        print_mci_error("Ошибка открытия файла", err);
        return;
    }
    
    g_track_open = 1;
    err = apply_volume_to_open_track();
    if (err != 0) {
        print_mci_error("Ошибка применения громкости", err);
    }

    if (get_current_track_duration_ms(&duration_ms)) {
        format_duration(duration_ms, duration_text, sizeof(duration_text));
    }

    // Запускаем воспроизведение
    err = mciSendStringA("play track", NULL, 0, NULL);
    if (err != 0) {
        print_mci_error("Ошибка воспроизведения файла", err);
        stop_music();
        return;
    }
    g_is_paused = 0;
    g_last_track_start_tick = GetTickCount();
    
    set_status("[▶] Играет: %s - %s (%s)", pl->current->artist, pl->current->title, duration_text);
}
// 6. Следующий трек (с закольцовкой)
void play_next(Playlist* pl) {
    if (pl->current == NULL) return;

    // Если есть следующий, переходим к нему. Иначе — возвращаемся в начало (head)
    if (pl->current->next != NULL) {
        pl->current = pl->current->next;
    } else {
        pl->current = pl->head; // Плейлист начался заново
    }
    play_current(pl);
}

// 7. Предыдущий трек (с закольцовкой)
void play_prev(Playlist* pl) {
    if (pl->current == NULL) return;

    // Если есть предыдущий, переходим к нему. Иначе — идем в самый конец (tail)
    if (pl->current->prev != NULL) {
        pl->current = pl->current->prev;
    } else {
        pl->current = pl->tail; // Перемотали в конец
    }
    play_current(pl);
}

// 8. Красивый вывод плейлиста
void print_playlist(Playlist* pl) {
    clear_panel();

    if (pl->head == NULL) {
        set_status("[!] Плейлист пуст.");
        return;
    }

    append_panel("=== ВАШ ПЛЕЙЛИСТ (%d треков) ===\n", pl->size);
    Track* temp = pl->head;
    int index = 1;

    // Идем по списку от head до tail
    while (temp != NULL) {
        // Выделяем трек, который сейчас играет
        if (temp == pl->current) {
            append_panel(" >>> %d. %s - %s <<<\n", index, temp->artist, temp->title);
        } else {
            append_panel("     %d. %s - %s\n", index, temp->artist, temp->title);
        }
        temp = temp->next;
        index++;
    }
    append_panel("=================================\n");
    set_status("[INFO] Плейлист показан.");
}

// 9. Интерактивное добавление трека пользователем (с очисткой кавычек)
void add_track_interactive(Playlist* pl) {
    char title[TITLE_SIZE], artist[ARTIST_SIZE], filepath[PATH_SIZE];
    
    system("cls");
    printf("--- Добавление нового трека ---\n\n");

    int c;
    while ((c = getchar()) != '\n' && c != EOF); // Очистка буфера

    printf("Введите исполнителя: ");
    fgets(artist, sizeof(artist), stdin);
    artist[strcspn(artist, "\n")] = 0;

    printf("Введите название трека: ");
    fgets(title, sizeof(title), stdin);
    title[strcspn(title, "\n")] = 0;

    printf("Введите полный путь к файлу (.mp3): ");
    fgets(filepath, sizeof(filepath), stdin);
    filepath[strcspn(filepath, "\n")] = 0;

    // --- УДАЛЕНИЕ КАВЫЧЕК, если они есть ---
    strip_surrounding_quotes(filepath);

    if (artist[0] == '\0' || title[0] == '\0' || filepath[0] == '\0') {
        clear_panel();
        set_status("[!] Исполнитель, название и путь к файлу не должны быть пустыми.");
        return;
    }

    const char* ext = strrchr(filepath, '.');
    if (ext == NULL || _stricmp(ext, ".mp3") != 0) {
        clear_panel();
        set_status("[!] Можно добавить только .mp3 файл.");
        return;
    }

    if (!file_exists_utf8(filepath)) {
        clear_panel();
        set_status("[!] Файл не найден: %s", filepath);
        return;
    }

    add_track_end(pl, title, artist, filepath);
    clear_panel();
    set_status("[+] Трек '%s - %s' успешно добавлен!", artist, title);
}
// 10. Удаление трека по номеру
void remove_track_by_index(Playlist* pl, int index) {
    clear_panel();

    if (pl->head == NULL || index < 1 || index > pl->size) {
        set_status("[!] Неверный номер трека.");
        return;
    }

    Track* current = pl->head;
    for (int i = 1; i < index; i++) {
        current = current->next;
    }

    // Если удаляем трек, который сейчас играет, останавливаем музыку
    if (current == pl->current) {
        stop_music();
        pl->current = current->next != NULL ? current->next : pl->head;
        if (pl->size == 1) pl->current = NULL; // Если это был единственный трек
    }

    // Перевязываем указатели (классика двусвязного списка)
    if (current->prev != NULL) {
        current->prev->next = current->next;
    } else {
        pl->head = current->next; // Если удаляем первый элемент
    }

    if (current->next != NULL) {
        current->next->prev = current->prev;
    } else {
        pl->tail = current->prev; // Если удаляем последний элемент
    }

    free(current); // Освобождаем память
    pl->size--;
    set_status("[+] Трек #%d удален из плейлиста.", index);
}

// 11. Сохранение плейлиста в текстовый файл
void save_playlist(Playlist* pl, const char* filename) {
    clear_panel();

    FILE* file = fopen(filename, "w");
    if (!file) {
        set_status("[!] Ошибка: Не удалось создать файл %s", filename);
        return;
    }

    Track* temp = pl->head;
    while (temp != NULL) {
        // Записываем данные через разделитель |
        fprintf(file, "%s|%s|%s\n", temp->artist, temp->title, temp->filepath);
        temp = temp->next;
    }
    fclose(file);
    set_status("[+] Плейлист успешно сохранен в %s", filename);
}

// 12. Загрузка плейлиста из файла
void load_playlist(Playlist* pl, const char* filename) {
    clear_panel();

    FILE* file = fopen(filename, "r");
    if (!file) {
        set_status("[!] Ошибка: Файл %s не найден.", filename);
        return;
    }

    char line[PLAYLIST_LINE_SIZE];
    int count = 0;
    int skipped = 0;

    stop_music();
    clear_playlist(pl);

    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\n")] = 0; // Удаляем перенос строки
        
        // Разбиваем строку по разделителю |
        char* artist = strtok(line, "|");
        char* title = strtok(NULL, "|");
        char* filepath = strtok(NULL, "|");

        if (artist && title && filepath) {
            if (file_exists_utf8(filepath)) {
                add_track_end(pl, title, artist, filepath);
                count++;
            } else {
                skipped++;
            }
        }
    }
    fclose(file);
    set_status("[+] Загружено %d треков из %s. Пропущено недоступных файлов: %d.", count, filename, skipped);
}

// 13. Полная очистка памяти (защита от утечек при выходе)
void clear_playlist(Playlist* pl) {
    Track* current = pl->head;
    while (current != NULL) {
        Track* next_track = current->next;
        free(current);
        current = next_track;
    }
    pl->head = NULL;
    pl->tail = NULL;
    pl->current = NULL;
    pl->size = 0;
}

// 14. Загрузка аудиофайлов (.mp3) из папки
void load_from_folder(Playlist* pl) {
    char folder_path[PATH_SIZE];
    int c;

    system("cls");
    printf("--- Загрузка папки ---\n\n");

    while ((c = getchar()) != '\n' && c != EOF); 

    printf("Введите полный путь к папке: ");
    fgets(folder_path, sizeof(folder_path), stdin);
    folder_path[strcspn(folder_path, "\n")] = 0;

    strip_surrounding_quotes(folder_path);

    if (folder_path[0] == '\0') {
        clear_panel();
        set_status("[!] Ошибка: путь к папке не должен быть пустым.");
        return;
    }

    // ТЕПЕРЬ ИЩЕМ ВООБЩЕ ВСЕ ФАЙЛЫ (*.*)
    char search_path[COMMAND_SIZE];
    size_t len = strlen(folder_path);
    int written;
    if (len > 0 && folder_path[len - 1] != '\\' && folder_path[len - 1] != '/') {
        written = snprintf(search_path, sizeof(search_path), "%s\\*.*", folder_path);
    } else {
        written = snprintf(search_path, sizeof(search_path), "%s*.*", folder_path);
    }

    if (written < 0 || written >= (int)sizeof(search_path)) {
        clear_panel();
        set_status("[!] Ошибка: путь к папке слишком длинный.");
        return;
    }

    wchar_t wsearch_path[COMMAND_SIZE];
    if (MultiByteToWideChar(CP_UTF8, 0, search_path, -1, wsearch_path, COMMAND_SIZE) == 0) {
        clear_panel();
        set_status("[!] Ошибка преобразования пути в Unicode.");
        return;
    }

    WIN32_FIND_DATAW findFileData;
    HANDLE hFind = FindFirstFileW(wsearch_path, &findFileData);

    if (hFind == INVALID_HANDLE_VALUE) {
        clear_panel();
        set_status("[!] Ошибка: Папка не найдена или путь неверный.");
        return;
    }

    int count = 0;
    do {
        if (!(findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
            char filename_utf8[PATH_SIZE];
            if (WideCharToMultiByte(CP_UTF8, 0, findFileData.cFileName, -1, filename_utf8, sizeof(filename_utf8), NULL, NULL) == 0) {
                continue;
            }

            // ПРОВЕРЯЕМ РАСШИРЕНИЕ ФАЙЛА
            const char* ext = strrchr(filename_utf8, '.');
            if (ext != NULL && _stricmp(ext, ".mp3") == 0) {
                
                char full_filepath[PATH_SIZE];
                if (len > 0 && folder_path[len - 1] != '\\' && folder_path[len - 1] != '/') {
                    written = snprintf(full_filepath, sizeof(full_filepath), "%s\\%s", folder_path, filename_utf8);
                } else {
                    written = snprintf(full_filepath, sizeof(full_filepath), "%s%s", folder_path, filename_utf8);
                }

                if (written < 0 || written >= (int)sizeof(full_filepath)) {
                    continue;
                }

                char title[TITLE_SIZE];
                char artist[ARTIST_SIZE];

                // Для MP3 пробуем вытащить теги
                if (get_id3v1_tags(full_filepath, title, artist)) {
                    // Теги успешно загружены (ничего делать не надо, переменные уже заполнены)
                } else {
                    // Если MP3 без тегов, берем название из файла
                    copy_string(title, sizeof(title), filename_utf8);
                    char* dot = strrchr(title, '.');
                    if (dot) *dot = '\0';
                    copy_string(artist, sizeof(artist), "Unknown");
                }

                add_track_end(pl, title, artist, full_filepath);
                count++;
            }
        }
    } while (FindNextFileW(hFind, &findFileData) != 0);

    FindClose(hFind);
    clear_panel();
    set_status("[+] Успешно загружено %d треков (.mp3)!", count);
}

// Вспомогательная функция для удаления лишних пробелов в конце строки (теги часто забивают пробелами до 30 символов)
void trim_trailing_spaces(char* str) {
    size_t len = strlen(str);
    while (len > 0) {
        char last = str[len - 1];
        if (last != ' ' && last != '\t' && last != '\n' && last != '\r') {
            break;
        }
        str[len - 1] = '\0';
        len--;
    }
}

// 15. ПАРСЕР ТЕГОВ: Чтение бинарного файла и извлечение ID3v1
int get_id3v1_tags(const char* filepath, char* out_title, char* out_artist) {
    // Переводим путь в Unicode, чтобы fopen смог открыть файл с русским названием
    wchar_t wfilepath[PATH_SIZE];
    if (MultiByteToWideChar(CP_UTF8, 0, filepath, -1, wfilepath, PATH_SIZE) == 0) {
        return 0;
    }

    // Открываем файл в режиме чтения бинарных данных ("rb" - read binary). Используем _wfopen для Unicode путей в Windows
    FILE* file = _wfopen(wfilepath, L"rb");
    if (!file) return 0; // Файл не открылся

    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return 0;
    }

    long file_size = ftell(file);
    if (file_size < 128) {
        fclose(file);
        return 0;
    }

    // Прыгаем в самый конец файла, отступив 128 байт назад!
    if (fseek(file, -128, SEEK_END) != 0) {
        fclose(file);
        return 0;
    }
    
    char buffer[128];
    // Читаем эти 128 байт в наш буфер
    if (fread(buffer, 1, 128, file) != 128) {
        fclose(file);
        return 0;
    }
    fclose(file);

    // Проверяем, есть ли метка "TAG"
    if (strncmp(buffer, "TAG", 3) == 0) {
        char raw_title[31] = {0};
        char raw_artist[31] = {0};

        // Копируем 30 байт названия и 30 байт исполнителя
        memcpy(raw_title, buffer + 3, 30);
        memcpy(raw_artist, buffer + 33, 30);

        trim_trailing_spaces(raw_title);
        trim_trailing_spaces(raw_artist);

        // МАГИЯ КОДИРОВОК: Теги в MP3 в России обычно хранятся в кодировке Windows-1251 (ANSI).
        // А наша программа работает в UTF-8. Нам нужно их перевести, иначе будут иероглифы.
        wchar_t wtitle[256], wartist[256];
        if (MultiByteToWideChar(1251, 0, raw_title, -1, wtitle, 256) == 0 ||
            MultiByteToWideChar(1251, 0, raw_artist, -1, wartist, 256) == 0) {
            return 0;
        }

        // Теперь из Unicode (WideChar) переводим в наш UTF-8
        if (WideCharToMultiByte(CP_UTF8, 0, wtitle, -1, out_title, TITLE_SIZE, NULL, NULL) == 0 ||
            WideCharToMultiByte(CP_UTF8, 0, wartist, -1, out_artist, ARTIST_SIZE, NULL, NULL) == 0) {
            return 0;
        }

        // Если теги оказались пустыми (просто пробелы), вернем 0
        if (strlen(out_title) == 0 || strlen(out_artist) == 0) return 0;

        return 1; // Успешно нашли и прочитали!
    }
    
    return 0; // Метки "TAG" нет
}
// 16. Пауза и продолжение
void toggle_pause() {
    clear_panel();

    if (!g_track_open) {
        set_status("[!] Сейчас нет открытого трека.");
        return;
    }

    MCIERROR err;
    if (!g_is_paused) {
        err = mciSendStringA("pause track", NULL, 0, NULL);
        if (err != 0) {
            print_mci_error("Ошибка постановки на паузу", err);
            return;
        }
        set_status("[PAUSE] Пауза");
        g_is_paused = 1;
    } else {
        err = mciSendStringA("resume track", NULL, 0, NULL);
        if (err != 0) {
            print_mci_error("Ошибка продолжения воспроизведения", err);
            return;
        }
        set_status("[PLAY] Воспроизведение продолжено");
        g_is_paused = 0;
    }
}

// 17. Сортировка плейлиста по названию трека
void sort_playlist(Playlist* pl) {
    clear_panel();

    if (pl->head == NULL || pl->head->next == NULL) {
        set_status("[!] В плейлисте недостаточно треков для сортировки.");
        return;
    }

    Track* sorted_head = NULL;
    Track* sorted_tail = NULL;
    Track* node = pl->head;

    while (node != NULL) {
        Track* next = node->next;
        node->prev = NULL;
        node->next = NULL;

        if (sorted_head == NULL) {
            sorted_head = node;
            sorted_tail = node;
        } else if (_stricmp(node->title, sorted_head->title) < 0) {
            node->next = sorted_head;
            sorted_head->prev = node;
            sorted_head = node;
        } else {
            Track* position = sorted_head;
            while (position->next != NULL && _stricmp(position->next->title, node->title) <= 0) {
                position = position->next;
            }

            node->next = position->next;
            node->prev = position;

            if (position->next != NULL) {
                position->next->prev = node;
            } else {
                sorted_tail = node;
            }

            position->next = node;
        }

        node = next;
    }

    pl->head = sorted_head;
    pl->tail = sorted_tail;

    print_playlist(pl);
    set_status("[+] Плейлист успешно отсортирован по алфавиту (от А до Я)!");
}

void search_tracks(Playlist* pl) {
    char query[TITLE_SIZE];
    Track* temp;
    int index = 1;
    int found = 0;
    int c;

    system("cls");
    printf("--- Поиск треков ---\n\n");

    while ((c = getchar()) != '\n' && c != EOF);

    printf("Введите слово для поиска: ");
    fgets(query, sizeof(query), stdin);
    query[strcspn(query, "\n")] = 0;

    clear_panel();

    if (query[0] == '\0') {
        set_status("[!] Слово для поиска не должно быть пустым.");
        return;
    }

    append_panel("=== РЕЗУЛЬТАТЫ ПОИСКА: %s ===\n", query);

    temp = pl->head;
    while (temp != NULL) {
        if (contains_ignore_case_utf8(temp->title, query) || contains_ignore_case_utf8(temp->artist, query)) {
            append_panel("     %d. %s - %s\n", index, temp->artist, temp->title);
            found++;
        }

        temp = temp->next;
        index++;
    }

    if (found == 0) {
        append_panel("Совпадений не найдено.\n");
    }

    append_panel("=================================\n");
    set_status("[INFO] Поиск завершен. Найдено совпадений: %d.", found);
}

void shuffle_playlist(Playlist* pl) {
    Track** tracks;
    Track* temp;
    int i;

    clear_panel();

    if (pl->size < 2) {
        set_status("[!] В плейлисте недостаточно треков для перемешивания.");
        return;
    }

    tracks = (Track**)malloc(sizeof(*tracks) * pl->size);
    if (tracks == NULL) {
        set_status("[!] Ошибка: не удалось выделить память для перемешивания.");
        return;
    }

    temp = pl->head;
    for (i = 0; i < pl->size; i++) {
        tracks[i] = temp;
        temp = temp->next;
    }

    for (i = pl->size - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        Track* swap = tracks[i];
        tracks[i] = tracks[j];
        tracks[j] = swap;
    }

    for (i = 0; i < pl->size; i++) {
        tracks[i]->prev = i > 0 ? tracks[i - 1] : NULL;
        tracks[i]->next = i < pl->size - 1 ? tracks[i + 1] : NULL;
    }

    pl->head = tracks[0];
    pl->tail = tracks[pl->size - 1];
    free(tracks);

    print_playlist(pl);
    set_status("[+] Плейлист перемешан.");
}

DWORD WINAPI auto_next_monitor(LPVOID parameter) {
    Playlist* pl = (Playlist*)parameter;

    while (InterlockedCompareExchange(&g_auto_next_running, 1, 1) == 1) {
        Sleep(AUTO_NEXT_POLL_MS);

        lock_player();

        if (g_track_open && !g_is_paused && g_last_track_start_tick != 0 &&
            GetTickCount() - g_last_track_start_tick >= AUTO_NEXT_START_GRACE_MS) {
            char mode[32] = "";
            MCIERROR err = mciSendStringA("status track mode", mode, sizeof(mode), NULL);

            if (err == 0 && strcmp(mode, "stopped") == 0 && pl->current != NULL) {
                set_status("[AUTO] Трек закончился. Включаю следующий.");
                play_next(pl);
            }
        }

        unlock_player();
    }

    return 0;
}

static void start_auto_next_monitor(Playlist* pl) {
    InterlockedExchange(&g_auto_next_running, 1);
    g_auto_next_thread = CreateThread(NULL, 0, auto_next_monitor, pl, 0, NULL);
    if (g_auto_next_thread == NULL) {
        InterlockedExchange(&g_auto_next_running, 0);
        set_status("[!] Не удалось запустить автопереход на следующий трек.");
    }
}

static void stop_auto_next_monitor(void) {
    if (g_auto_next_thread == NULL) return;

    InterlockedExchange(&g_auto_next_running, 0);
    WaitForSingleObject(g_auto_next_thread, INFINITE);
    CloseHandle(g_auto_next_thread);
    g_auto_next_thread = NULL;
}

// --- ИНТЕРФЕЙС ---
void print_menu() {
    printf("\n[ УПРАВЛЕНИЕ ПЛЕЕРОМ ]\n");
    printf("1. Играть         | 6. Показать плейлист\n");
    printf("2. Пауза          | 7. Добавить трек / Импорт папки\n");
    printf("3. Стоп           | 8. Удалить трек\n");
    printf("4. Следующий      | 9. Отсортировать по алфавиту\n");
    printf("5. Предыдущий     | 10. Сохр. / Загр. в файл\n");
    printf("11. Поиск         | 12. Shuffle\n");
    printf("+. Громкость выше | -. Громкость ниже (сейчас %d%%)\n", g_volume / 10);
    printf("0. Выход\n");
    printf("Ваш выбор: ");
}

void render_screen() {
    system("cls");

    printf("[ СТАТУС ]\n");
    printf("%s\n\n", g_status_message);

    if (g_panel_text[0] != '\0') {
        printf("%s\n", g_panel_text);
    }

    print_menu();
}

#ifndef MUSICPLAYER_TEST
int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    srand((unsigned int)time(NULL));
    InitializeCriticalSection(&g_player_lock);
    g_player_lock_ready = 1;

    Playlist my_playlist;
    init_playlist(&my_playlist);
    load_settings();

    if (file_exists_utf8(DEFAULT_PLAYLIST_FILE)) {
        load_playlist(&my_playlist, DEFAULT_PLAYLIST_FILE);
    } else {
        set_status("Готово. Автосохраненный плейлист пока не найден.");
    }

    start_auto_next_monitor(&my_playlist);

    char choice[MENU_INPUT_SIZE];
    int running = 1;

    do {
        lock_player();
        render_screen();
        unlock_player();

        if (scanf("%15s", choice) != 1) break;

        lock_player();

        if (strcmp(choice, "1") == 0) {
            play_current(&my_playlist);
        } else if (strcmp(choice, "2") == 0) {
            toggle_pause();
        } else if (strcmp(choice, "3") == 0) {
            stop_music();
            clear_panel();
            set_status("[STOP] Музыка остановлена.");
        } else if (strcmp(choice, "4") == 0) {
            play_next(&my_playlist);
        } else if (strcmp(choice, "5") == 0) {
            play_prev(&my_playlist);
        } else if (strcmp(choice, "6") == 0) {
            print_playlist(&my_playlist);
        } else if (strcmp(choice, "7") == 0) {
            printf("1 - Добавить один трек, 2 - Загрузить папку: ");
            int sub7;
            if (scanf("%d", &sub7) == 1) {
                if (sub7 == 1) add_track_interactive(&my_playlist);
                else if (sub7 == 2) load_from_folder(&my_playlist);
            }
        } else if (strcmp(choice, "8") == 0) {
            print_playlist(&my_playlist);
            render_screen();
            if (my_playlist.size > 0) {
                printf("Введите номер трека для удаления: ");
                int index;
                if (scanf("%d", &index) == 1) remove_track_by_index(&my_playlist, index);
            }
        } else if (strcmp(choice, "9") == 0) {
            sort_playlist(&my_playlist);
        } else if (strcmp(choice, "10") == 0) {
            printf("1 - Сохранить, 2 - Загрузить: ");
            int sub10;
            if (scanf("%d", &sub10) == 1) {
                if (sub10 == 1) save_playlist(&my_playlist, DEFAULT_PLAYLIST_FILE);
                else if (sub10 == 2) load_playlist(&my_playlist, DEFAULT_PLAYLIST_FILE);
            }
        } else if (strcmp(choice, "11") == 0) {
            search_tracks(&my_playlist);
        } else if (strcmp(choice, "12") == 0) {
            shuffle_playlist(&my_playlist);
        } else if (strcmp(choice, "+") == 0) {
            increase_volume();
        } else if (strcmp(choice, "-") == 0) {
            decrease_volume();
        } else if (strcmp(choice, "0") == 0) {
            running = 0;
        } else {
            clear_panel();
            set_status("[!] Неверный выбор.");
        }

        unlock_player();
    } while (running);

    stop_auto_next_monitor();

    lock_player();
    save_playlist(&my_playlist, DEFAULT_PLAYLIST_FILE);
    save_settings();
    stop_music();
    clear_playlist(&my_playlist);
    unlock_player();

    if (g_player_lock_ready) {
        DeleteCriticalSection(&g_player_lock);
        g_player_lock_ready = 0;
    }

    system("cls");
    printf("Выход...\n");

    return 0;
}
#endif
```
