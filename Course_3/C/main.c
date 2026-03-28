#include "raylib.h"
#include <math.h>
#include <stdio.h>
#include <stdbool.h>

// --- КОНСТАНТЫ И СТРУКТУРЫ ---
const double G = 6.674e-11;
#define MAX_STARS 500
#define MAX_TRAIL 2000

typedef struct { double x, y; } Vec2D;

typedef struct {
    char name[20];
    double mass;
    double radius;
    Vec2D pos;
    Vec2D vel;
    Color color;
} Body;

// --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ СОСТОЯНИЯ (для простоты) ---
Body earth, ship;
bool crashed = false;
bool paused = false;
double scale = 2000000.0;
int timeWarp = 1;

Vec2D trail[MAX_TRAIL];
int trailCount = 0;
Vector2 stars[MAX_STARS];
float starSizes[MAX_STARS];

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

// Проекция координат Мир -> Экран
Vector2 WorldToScreen(Vec2D worldPos, int screenW, int screenH) {
    return (Vector2){
        (float)(screenW / 2.0 + worldPos.x / scale),
        (float)(screenH / 2.0 - worldPos.y / scale) // Ось Y инвертирована для математической корректности
    };
}

// Сброс симуляции
void ResetSim(double v_start) {
    earth = (Body){ "Earth", 5.972e24, 6371000.0, {0,0}, {0,0}, BLUE };
    ship = (Body){ "Ship", 50000.0, 100.0, {earth.radius + 384400000.0, 0}, {0, v_start}, LIGHTGRAY };
    trailCount = 0;
    crashed = false;
    paused = true; // Начинаем на паузе
}

// --- ОСНОВНЫЕ ФУНКЦИИ СИМУЛЯТОРА ---

void HandleInput(double* v_start) {
    // Зум
    float wheel = GetMouseWheelMove();
    if (wheel != 0) {
        scale -= wheel * (scale * 0.15);
        if (scale < 10000.0) scale = 10000.0;
    }

    // Управление скоростью запуска
    if (IsKeyPressed(KEY_UP)) *v_start += 50.0;
    if (IsKeyPressed(KEY_DOWN)) *v_start -= 50.0;

    // Time Warp
    if (IsKeyPressed(KEY_RIGHT)) timeWarp *= 2;
    if (IsKeyPressed(KEY_LEFT)) timeWarp /= 2;
    if (timeWarp < 1) timeWarp = 1;
    if (timeWarp > 1024) timeWarp = 1024;

    // Пауза и Рестарт
    if (IsKeyPressed(KEY_SPACE)) paused = !paused;
    if (IsKeyPressed(KEY_R)) ResetSim(*v_start);
    if (IsKeyPressed(KEY_F)) ToggleFullscreen();
}

void UpdatePhysics() {
    if (paused || crashed) return;

    for (int i = 0; i < timeWarp * 10; i++) { // 10 шагов для стабильности
        double dx = earth.pos.x - ship.pos.x;
        double dy = earth.pos.y - ship.pos.y;
        double r = sqrt(dx*dx + dy*dy);

        if (r <= earth.radius + ship.radius) {
            crashed = true;
            paused = true;
            return;
        }

        // Гравитация
        double acc_g = (G * earth.mass) / (r * r);
        ship.vel.x += acc_g * (dx / r) * 100.0;
        ship.vel.y += acc_g * (dy / r) * 100.0;

        // Двигатели (W, A, S, D)
        double thrust_acc = 10.0 / ship.mass; // Тяга 10Н
        double speed = sqrt(ship.vel.x*ship.vel.x + ship.vel.y*ship.vel.y);
        
        if (speed > 0) { // Защита от деления на ноль
            if (IsKeyDown(KEY_W)) { // Prograde (вперед)
                ship.vel.x += thrust_acc * (ship.vel.x / speed) * 100.0;
                ship.vel.y += thrust_acc * (ship.vel.y / speed) * 100.0;
            }
            if (IsKeyDown(KEY_S)) { // Retrograde (назад)
                ship.vel.x -= thrust_acc * (ship.vel.x / speed) * 100.0;
                ship.vel.y -= thrust_acc * (ship.vel.y / speed) * 100.0;
            }
        }
        
        ship.pos.x += ship.vel.x * 100.0;
        ship.pos.y += ship.vel.y * 100.0;
    }
}

void DrawScene(int sw, int sh) {
    // Параллакс-звезды
    for (int i = 0; i < MAX_STARS; i++) {
        Vector2 starPos = WorldToScreen((Vec2D){stars[i].x, stars[i].y}, sw, sh);
        DrawCircleV(starPos, starSizes[i], Fade(WHITE, 0.7f));
    }
    
    // Траектория
    for (int i = 0; i < trailCount; i++) {
        DrawCircleV(WorldToScreen(trail[i], sw, sh), 1, Fade(GREEN, 0.4f));
    }

    // Земля
    Vector2 earthPos = WorldToScreen(earth.pos, sw, sh);
    float earthRadius = (float)(earth.radius / scale);
    DrawCircleGradient(earthPos.x, earthPos.y, earthRadius * 1.5f, Fade(BLUE, 0.4f), BLANK);
    DrawCircleV(earthPos, earthRadius < 2.0f ? 2.0f : earthRadius, DARKBLUE);

    // Корабль
    Vector2 shipPos = WorldToScreen(ship.pos, sw, sh);
    float shipRadius = (float)(ship.radius / scale * 100); // Увеличим для видимости
    
    // Вектор скорости
    Vector2 velVector = WorldToScreen((Vec2D){ship.pos.x + ship.vel.x*scale*0.1, ship.pos.y + ship.vel.y*scale*0.1}, sw, sh);
    DrawLineEx(shipPos, velVector, 2, YELLOW);

    // Пламя двигателя
    if (!paused && !crashed && (IsKeyDown(KEY_W) || IsKeyDown(KEY_S))) {
        DrawCircleGradient(shipPos.x, shipPos.y, shipRadius * 2.5f, Fade(ORANGE, 0.8f), BLANK);
    }
    
    DrawCircleV(shipPos, shipRadius < 2.0f ? 2.0f : shipRadius, crashed ? RED : LIGHTGRAY);
}

void DrawHUD(int sw, int sh, double v_start) {
    double speed = sqrt(ship.vel.x*ship.vel.x + ship.vel.y*ship.vel.y);
    double altitude = sqrt(ship.pos.x*ship.pos.x + ship.pos.y*ship.pos.y) - earth.radius;

    DrawRectangle(0, 0, 420, sh, Fade(BLACK, 0.8f));
    DrawRectangleLines(0, 0, 420, sh, SKYBLUE);

    DrawText("ORBITAL COMMAND v3.0", 20, 20, 30, SKYBLUE);
    DrawText("----------------------", 20, 60, 30, SKYBLUE);

    DrawText("MISSION CONTROL", 20, 100, 20, GREEN);
    DrawText(TextFormat("Launch Velocity: %.0f m/s", v_start), 30, 130, 20, WHITE);
    DrawText(TextFormat("Time Warp: x%d", timeWarp), 30, 160, 20, WHITE);

    DrawText("SHIP TELEMETRY", 20, 220, 20, GREEN);
    DrawText(TextFormat("Speed: %.1f km/s", speed / 1000.0), 30, 250, 20, WHITE);
    DrawText(TextFormat("Altitude: %.0f km", altitude / 1000.0), 30, 280, 20, WHITE);
    
    char* status = crashed ? "IMPACT" : (paused ? "PAUSED" : "NOMINAL");
    Color statusColor = crashed ? RED : (paused ? YELLOW : GREEN);
    DrawText(TextFormat("System Status: %s", status), 20, sh-50, 25, statusColor);
}

int main(void) {
    int screenW = 1600;
    int screenH = 900;
    SetConfigFlags(FLAG_WINDOW_RESIZABLE | FLAG_MSAA_4X_HINT);
    InitWindow(screenW, screenH, "Sci-Fi Orbital Mechanics v3.0");
    SetTargetFPS(60);

    // Генерация звезд
    for (int i = 0; i < MAX_STARS; i++) {
        stars[i].x = GetRandomValue(-screenW * 50, screenW * 50);
        stars[i].y = GetRandomValue(-screenH * 50, screenH * 50);
        starSizes[i] = (float)GetRandomValue(1, 3);
    }
    
    double v_start = 1022.0; 
    ResetSim(v_start);

    while (!WindowShouldClose()) {
        screenW = GetScreenWidth();
        screenH = GetScreenHeight();

        // 1. Логика
        HandleInput(&v_start);
        UpdatePhysics();

        // 2. Запись хвоста (только если не на паузе)
        if (!paused) {
            if (trailCount < MAX_TRAIL) {
                trail[trailCount++] = ship.pos;
            } else {
                for(int i=0; i<MAX_TRAIL-1; i++) trail[i] = trail[i+1];
                trail[MAX_TRAIL-1] = ship.pos;
            }
        }
        
        // 3. Рисование
        BeginDrawing();
            ClearBackground((Color){5, 5, 15, 255});
            DrawScene(screenW, screenH);
            DrawHUD(screenW, screenH, v_start);
        EndDrawing();
    }
    CloseWindow();
    return 0;
}