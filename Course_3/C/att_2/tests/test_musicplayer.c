#define MUSICPLAYER_TEST
#include "../main.c"

#include <direct.h>

static int tests_run = 0;
static int tests_failed = 0;
static int settings_was_backed_up = 0;
static const char* settings_backup_path = "tests\\settings_backup.tmp";

#define TEST_ASSERT(condition) do { \
    tests_run++; \
    if (!(condition)) { \
        tests_failed++; \
        printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #condition); \
    } \
} while (0)

static void reset_ui_state(void) {
    clear_panel();
    set_status("test");
}

static void reset_playlist(Playlist* pl) {
    stop_music();
    clear_playlist(pl);
    init_playlist(pl);
    reset_ui_state();
}

static void create_file(const char* path) {
    FILE* file = fopen(path, "wb");
    TEST_ASSERT(file != NULL);
    if (file != NULL) {
        fputs("test", file);
        fclose(file);
    }
}

static void backup_settings_file(void) {
    remove(settings_backup_path);
    if (rename(SETTINGS_FILE, settings_backup_path) == 0) {
        settings_was_backed_up = 1;
    }
}

static void restore_settings_file(void) {
    remove(SETTINGS_FILE);
    if (settings_was_backed_up) {
        rename(settings_backup_path, SETTINGS_FILE);
        settings_was_backed_up = 0;
    }
}

static void test_string_helpers(void) {
    char value1[PATH_SIZE] = "\"C:\\Music\\song.mp3\"";
    char value2[PATH_SIZE] = "\"C:\\Music\\song.mp3";
    char value3[PATH_SIZE] = "C:\\Music\\song.mp3";
    char copied[8];
    char duration[DURATION_TEXT_SIZE];

    strip_surrounding_quotes(value1);
    TEST_ASSERT(strcmp(value1, "C:\\Music\\song.mp3") == 0);

    strip_surrounding_quotes(value2);
    TEST_ASSERT(strcmp(value2, "C:\\Music\\song.mp3") == 0);

    strip_surrounding_quotes(value3);
    TEST_ASSERT(strcmp(value3, "C:\\Music\\song.mp3") == 0);

    copy_string(copied, sizeof(copied), "123456789");
    TEST_ASSERT(strcmp(copied, "1234567") == 0);

    format_duration(225000, duration, sizeof(duration));
    TEST_ASSERT(strcmp(duration, "03:45") == 0);

    format_duration(-1, duration, sizeof(duration));
    TEST_ASSERT(strcmp(duration, "--:--") == 0);
}

static void test_volume_helpers(void) {
    g_track_open = 0;
    g_volume = VOLUME_MAX;

    TEST_ASSERT(clamp_volume(-50) == VOLUME_MIN);
    TEST_ASSERT(clamp_volume(500) == 500);
    TEST_ASSERT(clamp_volume(2000) == VOLUME_MAX);

    decrease_volume();
    TEST_ASSERT(g_volume == 900);

    increase_volume();
    TEST_ASSERT(g_volume == 1000);
}

static void test_playlist_add_remove_and_clear(void) {
    Playlist pl;
    init_playlist(&pl);

    add_track_end(&pl, "Gamma", "Artist C", "c.mp3");
    add_track_end(&pl, "Alpha", "Artist A", "a.mp3");
    add_track_end(&pl, "Beta", "Artist B", "b.mp3");

    TEST_ASSERT(pl.size == 3);
    TEST_ASSERT(pl.head != NULL);
    TEST_ASSERT(pl.tail != NULL);
    TEST_ASSERT(pl.current == pl.head);
    TEST_ASSERT(strcmp(pl.head->title, "Gamma") == 0);
    TEST_ASSERT(strcmp(pl.tail->title, "Beta") == 0);
    TEST_ASSERT(pl.head->next->prev == pl.head);

    remove_track_by_index(&pl, 2);
    TEST_ASSERT(pl.size == 2);
    TEST_ASSERT(strcmp(pl.head->title, "Gamma") == 0);
    TEST_ASSERT(strcmp(pl.tail->title, "Beta") == 0);
    TEST_ASSERT(pl.head->next == pl.tail);
    TEST_ASSERT(pl.tail->prev == pl.head);

    clear_playlist(&pl);
    TEST_ASSERT(pl.size == 0);
    TEST_ASSERT(pl.head == NULL);
    TEST_ASSERT(pl.tail == NULL);
    TEST_ASSERT(pl.current == NULL);
}

static void test_sort_playlist_keeps_current_node(void) {
    Playlist pl;
    Track* original_current;
    init_playlist(&pl);

    add_track_end(&pl, "Gamma", "Artist C", "c.mp3");
    add_track_end(&pl, "Alpha", "Artist A", "a.mp3");
    add_track_end(&pl, "Beta", "Artist B", "b.mp3");
    pl.current = pl.tail;
    original_current = pl.current;

    sort_playlist(&pl);

    TEST_ASSERT(pl.size == 3);
    TEST_ASSERT(strcmp(pl.head->title, "Alpha") == 0);
    TEST_ASSERT(strcmp(pl.head->next->title, "Beta") == 0);
    TEST_ASSERT(strcmp(pl.tail->title, "Gamma") == 0);
    TEST_ASSERT(pl.current == original_current);
    TEST_ASSERT(strcmp(pl.current->title, "Beta") == 0);

    clear_playlist(&pl);
}

static void test_shuffle_playlist_preserves_nodes(void) {
    Playlist pl;
    Track* first;
    Track* second;
    Track* third;
    int seen_first = 0;
    int seen_second = 0;
    int seen_third = 0;
    Track* node;
    int count = 0;

    init_playlist(&pl);
    add_track_end(&pl, "One", "Artist", "1.mp3");
    add_track_end(&pl, "Two", "Artist", "2.mp3");
    add_track_end(&pl, "Three", "Artist", "3.mp3");

    first = pl.head;
    second = pl.head->next;
    third = pl.tail;
    pl.current = second;

    srand(1);
    shuffle_playlist(&pl);

    TEST_ASSERT(pl.size == 3);
    TEST_ASSERT(pl.current == second);
    TEST_ASSERT(pl.head->prev == NULL);
    TEST_ASSERT(pl.tail->next == NULL);

    for (node = pl.head; node != NULL; node = node->next) {
        if (node == first) seen_first = 1;
        if (node == second) seen_second = 1;
        if (node == third) seen_third = 1;
        if (node->next != NULL) TEST_ASSERT(node->next->prev == node);
        count++;
    }

    TEST_ASSERT(count == 3);
    TEST_ASSERT(seen_first && seen_second && seen_third);

    clear_playlist(&pl);
}

static void test_case_insensitive_search_helper(void) {
    TEST_ASSERT(contains_ignore_case_utf8("Night Song", "night"));
    TEST_ASSERT(contains_ignore_case_utf8("Artist Name", "NAME"));
    TEST_ASSERT(contains_ignore_case_utf8("Ночная песня", "ноч"));
    TEST_ASSERT(!contains_ignore_case_utf8("Artist Name", "album"));
}

static void test_file_exists_utf8(void) {
    create_file("tests\\exists_test.mp3");
    TEST_ASSERT(file_exists_utf8("tests\\exists_test.mp3"));
    TEST_ASSERT(!file_exists_utf8("tests\\missing_test.mp3"));
    remove("tests\\exists_test.mp3");
}

static void test_save_and_load_playlist_skip_missing_files(void) {
    Playlist source;
    Playlist loaded;

    init_playlist(&source);
    init_playlist(&loaded);

    create_file("tests\\load_ok_1.mp3");
    create_file("tests\\load_ok_2.mp3");

    add_track_end(&source, "First", "Artist 1", "tests\\load_ok_1.mp3");
    add_track_end(&source, "Missing", "Artist 2", "tests\\missing_song.mp3");
    add_track_end(&source, "Second", "Artist 3", "tests\\load_ok_2.mp3");

    save_playlist(&source, "tests\\playlist_test.txt");
    load_playlist(&loaded, "tests\\playlist_test.txt");

    TEST_ASSERT(loaded.size == 2);
    TEST_ASSERT(strcmp(loaded.head->title, "First") == 0);
    TEST_ASSERT(strcmp(loaded.tail->title, "Second") == 0);

    clear_playlist(&source);
    clear_playlist(&loaded);
    remove("tests\\playlist_test.txt");
    remove("tests\\load_ok_1.mp3");
    remove("tests\\load_ok_2.mp3");
}

static void test_settings_roundtrip(void) {
    int previous_volume = g_volume;

    g_volume = 300;
    save_settings();

    g_volume = 1000;
    load_settings();
    TEST_ASSERT(g_volume == 300);

    g_volume = previous_volume;
    remove(SETTINGS_FILE);
}

int main(void) {
    InitializeCriticalSection(&g_player_lock);
    g_player_lock_ready = 1;
    _mkdir("tests");
    backup_settings_file();

    reset_ui_state();

    test_string_helpers();
    test_volume_helpers();
    test_playlist_add_remove_and_clear();
    test_sort_playlist_keeps_current_node();
    test_shuffle_playlist_preserves_nodes();
    test_case_insensitive_search_helper();
    test_file_exists_utf8();
    test_save_and_load_playlist_skip_missing_files();
    test_settings_roundtrip();

    stop_music();
    restore_settings_file();
    DeleteCriticalSection(&g_player_lock);
    g_player_lock_ready = 0;

    printf("Tests run: %d\n", tests_run);
    printf("Tests failed: %d\n", tests_failed);

    return tests_failed == 0 ? 0 : 1;
}
