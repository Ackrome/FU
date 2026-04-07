#include "raylib.h"
#include <math.h>
#include <stdio.h>
#include <stdbool.h>
#include <assert.h>

// --- КОНСТАНТЫ ---
const double G = 6.674e-11;
#define MAX_BODIES 100 
#define TRAIL_LEN 400
#define PRED_LEN 800

// --- СТРУКТУРЫ ДАННЫХ ---
typedef struct { double x, y; } Vec2D;

typedef struct {
    char name[32];
    double mass;
    double radius;
    Color color;
    Vec2D pos;
    Vec2D vel;
    
    Vec2D trail[TRAIL_LEN];
    int trailIdx;
    Vec2D lastTrailPos; // НОВОЕ: Для отслеживания сглаживания хвоста
    
    Vec2D pred[PRED_LEN];
} Body;

static Body system[MAX_BODIES];
static Body sim[MAX_BODIES];
double camX = 0.0, camY = 0.0;
double scale = 1e9; 
double totalTime = 0.0; 
int numBodies = 0;

// ==========================================
// БЛОК ФУНКЦИЙ 
// ==========================================

Vector2 WorldToScreen(Vec2D worldPos, int sw, int sh) {
    return (Vector2){ (float)((worldPos.x - camX) / scale + sw / 2.0), (float)((worldPos.y - camY) / scale + sh / 2.0) };
}

Vec2D ScreenToWorld(Vector2 screenPos, int sw, int sh) {
    return (Vec2D){ (screenPos.x - sw / 2.0) * scale + camX, (screenPos.y - sh / 2.0) * scale + camY };
}

Vec2D CalculateOrbitalVelocity(Body parent, Vec2D targetPos) {
    double dx = targetPos.x - parent.pos.x;
    double dy = targetPos.y - parent.pos.y;
    double dist = sqrt(dx*dx + dy*dy);
    double v_mag = sqrt((G * parent.mass) / dist);
    return (Vec2D){ parent.vel.x + (dy / dist) * v_mag, parent.vel.y - (dx / dist) * v_mag };
}

Vec2D CalculateBarycenter(Body* bodies, int count) {
    Vec2D bary = {0, 0};
    double totalMass = 0;
    for(int i = 0; i < count; i++) {
        bary.x += bodies[i].pos.x * bodies[i].mass;
        bary.y += bodies[i].pos.y * bodies[i].mass;
        totalMass += bodies[i].mass;
    }
    if(totalMass > 0) { bary.x /= totalMass; bary.y /= totalMass; }
    return bary;
}

void StepPhysics(Body* bodies, int count, double dt) {
    Vec2D acc[MAX_BODIES] = {0};
    for(int i = 0; i < count; i++) {
        for(int j = 0; j < count; j++) {
            if(i == j) continue;
            double dx = bodies[j].pos.x - bodies[i].pos.x;
            double dy = bodies[j].pos.y - bodies[i].pos.y;
            double distSq = dx*dx + dy*dy;
            double dist = sqrt(distSq);
            
            if (dist < bodies[i].radius + bodies[j].radius) dist = bodies[i].radius + bodies[j].radius;
            
            double force = (G * bodies[j].mass) / distSq;
            acc[i].x += force * (dx / dist);
            acc[i].y += force * (dy / dist);
        }
    }
    for(int i = 0; i < count; i++) {
        bodies[i].vel.x += acc[i].x * dt;
        bodies[i].vel.y += acc[i].y * dt;
        bodies[i].pos.x += bodies[i].vel.x * dt;
        bodies[i].pos.y += bodies[i].vel.y * dt;
    }
}

void HandleCollisions(Body* bodies, int* count) {
    for(int i = 0; i < *count; i++) {
        for(int j = i + 1; j < *count; j++) {
            double dx = bodies[j].pos.x - bodies[i].pos.x;
            double dy = bodies[j].pos.y - bodies[i].pos.y;
            double dist = sqrt(dx*dx + dy*dy);
            
            if (dist < bodies[i].radius + bodies[j].radius) {
                double totalMass = bodies[i].mass + bodies[j].mass;
                bodies[i].vel.x = (bodies[i].vel.x * bodies[i].mass + bodies[j].vel.x * bodies[j].mass) / totalMass;
                bodies[i].vel.y = (bodies[i].vel.y * bodies[i].mass + bodies[j].vel.y * bodies[j].mass) / totalMass;
                bodies[i].pos.x = (bodies[i].pos.x * bodies[i].mass + bodies[j].pos.x * bodies[j].mass) / totalMass;
                bodies[i].pos.y = (bodies[i].pos.y * bodies[i].mass + bodies[j].pos.y * bodies[j].mass) / totalMass;
                
                bodies[i].radius = pow(pow(bodies[i].radius, 3) + pow(bodies[j].radius, 3), 1.0/3.0);
                bodies[i].mass = totalMass;
                sprintf(bodies[i].name, "Merged Anomaly");
                bodies[i].lastTrailPos = bodies[i].pos; // Обновляем точку старта хвоста при слиянии

                for (int k = j; k < *count - 1; k++) bodies[k] = bodies[k+1];
                (*count)--;
                j--; 
            }
        }
    }
}

// НОВОЕ: Умный прогноз, зависящий от масштаба камеры
void UpdatePredictions(Body* real_bodies, int count, double current_scale) {
    for(int i = 0; i < count; i++) sim[i] = real_bodies[i];
    
    // Чем дальше отдаляем камеру, тем шире шаг прогноза (чтобы охватить годы)
    double pred_dt = current_scale / 5000.0; 
    if (pred_dt < 60.0) pred_dt = 60.0; // Минимум 1 минута на шаг
    
    for(int step = 0; step < PRED_LEN; step++) {
        StepPhysics(sim, count, pred_dt);
        for(int i = 0; i < count; i++) real_bodies[i].pred[step] = sim[i].pos;
    }
}

void InitSolarSystem() {
    numBodies = 10;
    // Оставляем пустые поля для массивов, мы их инициализируем циклом ниже
    system[0] = (Body){"Sun", 1.989e30, 696340000.0, YELLOW, {0,0}, {0,0}};
    system[1] = (Body){"Mercury", 3.301e23, 2439000.0, GRAY, {57.9e9, 0}, {0, -47400.0}};
    system[2] = (Body){"Venus", 4.867e24, 6051000.0, ORANGE, {108.2e9, 0}, {0, -35000.0}};
    system[3] = (Body){"Earth", 5.972e24, 6371000.0, (Color){50,150,255,255}, {149.6e9, 0}, {0, -29780.0}};
    system[4] = (Body){"Moon", 7.342e22, 1737000.0, LIGHTGRAY, {149.6e9 + 384400000.0, 0}, {0, -29780.0 - 1022.0}};
    system[5] = (Body){"Mars", 6.417e23, 3389000.0, RED, {227.9e9, 0}, {0, -24100.0}};
    system[6] = (Body){"Jupiter", 1.898e27, 69911000.0, (Color){200,150,100,255}, {778.5e9, 0}, {0, -13100.0}};
    system[7] = (Body){"Saturn", 5.683e26, 58232000.0, GOLD, {1.432e12, 0}, {0, -9700.0}};
    system[8] = (Body){"Uranus", 8.681e25, 25362000.0, SKYBLUE, {2.867e12, 0}, {0, -6800.0}};
    system[9] = (Body){"Neptune", 1.024e26, 24622000.0, DARKBLUE, {4.495e12, 0}, {0, -5400.0}};
    
    // Инициализируем стартовые точки для хвостов
    for(int i = 0; i < numBodies; i++) {
        system[i].lastTrailPos = system[i].pos;
        system[i].trailIdx = 0;
    }
}

void RunTests() {
    printf("[TEST] Running Validations...\n");
    Body b1 = {"A", 10.0, 1.0, WHITE, {0,0}, {5.0, 0}};
    Body b2 = {"B", 10.0, 1.0, WHITE, {1.5, 0}, {-5.0, 0}}; // Измененная дистанция для теста
    Body testSystem[2] = {b1, b2};
    int tCount = 2;
    HandleCollisions(testSystem, &tCount);
    assert(tCount == 1); 
    assert(testSystem[0].vel.x == 0.0); 
    printf("[TEST] OK.\n");
}

int main(void) {
    RunTests(); 

    SetConfigFlags(FLAG_WINDOW_RESIZABLE | FLAG_MSAA_4X_HINT);
    InitWindow(1400, 900, "Orbital Sandbox (Smooth Physics Edition)");
    SetTargetFPS(60);

    InitSolarSystem();

    float exactTimeWarp = 1000.0f; // Для плавного разгона времени
    int timeWarp = 1000; 
    double fixed_dt = 100.0;
    bool isPaused = false;
    int focusIdx = 3; 

    bool isSpawning = false;
    Vector2 spawnStartScreen;
    double spawnMassExp = 24.0;

    while (!WindowShouldClose()) {
        int sw = GetScreenWidth();
        int sh = GetScreenHeight();

        // --- УПРАВЛЕНИЕ ---
        if (!isSpawning && GetMouseWheelMove() != 0) {
            scale -= GetMouseWheelMove() * (scale * 0.15);
            if (scale < 1000.0) scale = 1000.0; 
        }
        if (IsMouseButtonDown(MOUSE_BUTTON_RIGHT)) {
            Vector2 delta = GetMouseDelta();
            camX -= delta.x * scale;
            camY -= delta.y * scale;
            focusIdx = -1;
        }

        if (IsKeyPressed(KEY_TAB) && numBodies > 0) focusIdx = (focusIdx + 1) % numBodies;
        if (IsKeyPressed(KEY_SPACE)) isPaused = !isPaused;

        // ЭКСПОНЕНЦИАЛЬНОЕ УПРАВЛЕНИЕ ВРЕМЕНЕМ
        if (IsKeyDown(KEY_RIGHT) && exactTimeWarp < 1000000.0f) exactTimeWarp *= 1.03f;
        if (IsKeyDown(KEY_LEFT) && exactTimeWarp > 1.0f) exactTimeWarp /= 1.03f;
        timeWarp = (int)exactTimeWarp;
        if (timeWarp < 1) timeWarp = 1;

        // --- СОЗДАНИЕ ТЕЛ (ФИКС РОГАТКИ) ---
        if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            isSpawning = true;
            spawnStartScreen = GetMousePosition();
        }
        
        if (isSpawning) {
            float wheel = GetMouseWheelMove();
            if (wheel != 0) spawnMassExp += wheel * 0.5;
            if (spawnMassExp < 21) spawnMassExp = 21; // Минимум астероид Церера
            if (spawnMassExp > 33) spawnMassExp = 33; 

            if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT)) {
                if (numBodies < MAX_BODIES) {
                    Vec2D worldPos = ScreenToWorld(spawnStartScreen, sw, sh);
                    double vx = 0, vy = 0;

                    if (IsKeyDown(KEY_LEFT_SHIFT) && numBodies > 0) {
                        int targetParent = (focusIdx >= 0 && focusIdx < numBodies) ? focusIdx : 0;
                        Vec2D calcVel = CalculateOrbitalVelocity(system[targetParent], worldPos);
                        vx = calcVel.x;
                        vy = calcVel.y;
                    } 
                    else {
                        // Адекватные скорости для рогатки (150 м/с за каждый пиксель натяжения)
                        Vector2 mousePos = GetMousePosition();
                        vx = (spawnStartScreen.x - mousePos.x) * 150.0;
                        vy = (spawnStartScreen.y - mousePos.y) * 150.0;
                    }
                    
                    system[numBodies].mass = pow(10.0, spawnMassExp);
                    system[numBodies].radius = 6000000.0 * (spawnMassExp / 24.0);
                    system[numBodies].color = MAGENTA;
                    system[numBodies].pos = worldPos;
                    system[numBodies].vel = (Vec2D){vx, vy};
                    system[numBodies].trailIdx = 0;
                    system[numBodies].lastTrailPos = worldPos; // Инициализируем хвост
                    sprintf(system[numBodies].name, "Object-%d", numBodies);
                    
                    numBodies++;
                }
                isSpawning = false;
            }
        }

        if (focusIdx >= 0 && focusIdx < numBodies) {
            camX = system[focusIdx].pos.x;
            camY = system[focusIdx].pos.y;
        }

        // --- ФИЗИКА И СГЛАЖИВАНИЕ ---
        if (!isPaused) {
            // Квадрат минимальной дистанции для отрисовки точки хвоста (3 пикселя экрана)
            double min_dist_sq = (scale * 3.0) * (scale * 3.0); 

            for (int i = 0; i < timeWarp; i++) {
                StepPhysics(system, numBodies, fixed_dt);
                totalTime += fixed_dt;

                // Запись хвоста на основе ПРОЙДЕННОГО РАССТОЯНИЯ (гладкие орбиты!)
                for(int b = 0; b < numBodies; b++) {
                    double dx = system[b].pos.x - system[b].lastTrailPos.x;
                    double dy = system[b].pos.y - system[b].lastTrailPos.y;
                    
                    if (dx*dx + dy*dy > min_dist_sq) {
                        if (system[b].trailIdx < TRAIL_LEN) {
                            system[b].trail[system[b].trailIdx++] = system[b].pos;
                        } else {
                            // Сдвигаем старые точки
                            for(int k = 0; k < TRAIL_LEN - 1; k++) system[b].trail[k] = system[b].trail[k+1];
                            system[b].trail[TRAIL_LEN - 1] = system[b].pos;
                        }
                        system[b].lastTrailPos = system[b].pos;
                    }
                }
            }
            HandleCollisions(system, &numBodies);
            UpdatePredictions(system, numBodies, scale); // Прогноз теперь адаптивен
        }

        Vec2D barycenter = CalculateBarycenter(system, numBodies);

        // --- РИСОВАНИЕ ---
        BeginDrawing();
            ClearBackground((Color){ 5, 5, 15, 255 });

            for(int i = 0; i < numBodies; i++) {
                // Плавные линии прогноза
                for (int p = 0; p < PRED_LEN - 1; p += 2) {
                    DrawLineV(WorldToScreen(system[i].pred[p], sw, sh), WorldToScreen(system[i].pred[p+1], sw, sh), Fade(system[i].color, 0.2f));
                }
                // Плавные хвосты (соединенные линиями)
                for (int t = 0; t < system[i].trailIdx - 1; t++) {
                    DrawLineEx(WorldToScreen(system[i].trail[t], sw, sh), WorldToScreen(system[i].trail[t+1], sw, sh), 2.0f, Fade(system[i].color, 0.6f));
                }

                Vector2 screenPos = WorldToScreen(system[i].pos, sw, sh);
                float drawRadius = (float)(system[i].radius / scale);
                
                if (drawRadius < 3.0f) {
                    drawRadius = 3.0f;
                    DrawCircleLines(screenPos.x, screenPos.y, 8.0f, Fade(system[i].color, 0.5f));
                }
                if (i == 0 && drawRadius < 6.0f) drawRadius = 6.0f;

                DrawCircleGradient((int)screenPos.x, (int)screenPos.y, drawRadius * 2.0f, Fade(system[i].color, 0.5f), BLANK);
                DrawCircleV(screenPos, drawRadius, system[i].color);
                DrawText(system[i].name, screenPos.x + 10, screenPos.y - 10, 10, RAYWHITE);
            }

            Vector2 baryScreen = WorldToScreen(barycenter, sw, sh);
            DrawLine(baryScreen.x - 10, baryScreen.y, baryScreen.x + 10, baryScreen.y, GREEN);
            DrawLine(baryScreen.x, baryScreen.y - 10, baryScreen.x, baryScreen.y + 10, GREEN);

            // Интерактивный UI Создания
            if (isSpawning) {
                if (IsKeyDown(KEY_LEFT_SHIFT)) {
                    int targetParent = (focusIdx >= 0 && focusIdx < numBodies) ? focusIdx : 0;
                    Vector2 parentScreen = WorldToScreen(system[targetParent].pos, sw, sh);
                    DrawLineEx(parentScreen, spawnStartScreen, 1.0f, Fade(GREEN, 0.5f)); 
                    DrawCircleLines(spawnStartScreen.x, spawnStartScreen.y, 20, GREEN);
                    DrawText(TextFormat("AUTO-ORBIT: %s", system[targetParent].name), spawnStartScreen.x + 25, spawnStartScreen.y - 10, 15, GREEN);
                } else {
                    Vector2 mousePos = GetMousePosition();
                    // Вычисляем будущую скорость для отображения
                    double show_vx = (spawnStartScreen.x - mousePos.x) * 150.0;
                    double show_vy = (spawnStartScreen.y - mousePos.y) * 150.0;
                    double show_vel = sqrt(show_vx*show_vx + show_vy*show_vy);

                    DrawLineEx(spawnStartScreen, mousePos, 2.0f, RED);
                    DrawText("SLINGSHOT MODE", mousePos.x + 15, mousePos.y, 10, RED);
                    DrawText(TextFormat("Velocity: %.1f km/s", show_vel / 1000.0), mousePos.x + 15, mousePos.y + 25, 15, RED);
                }
                DrawText(TextFormat("Mass: 10^%.1f kg", spawnMassExp), spawnStartScreen.x - 50, spawnStartScreen.y - 30, 15, MAGENTA);
            }

            // HUD
            DrawRectangle(sw/2 - 150, 10, 300, 60, Fade(BLACK, 0.7f));
            DrawRectangleLines(sw/2 - 150, 10, 300, 60, DARKGRAY);
            DrawText(TextFormat("YEAR %d, DAY %d", (int)(totalTime/86400.0/365.25), (int)fmod(totalTime/86400.0, 365.25)), sw/2 - 90, 20, 20, WHITE);
            if (isPaused) DrawText("--- PAUSED ---", sw/2 - 60, 45, 15, RED);

            DrawRectangle(10, 10, 350, 160, Fade(BLACK, 0.8f));
            DrawRectangleLines(10, 10, 350, 160, DARKGRAY);
            DrawText("AEROSIGHT ORBITAL UI:", 20, 20, 15, MAGENTA);
            DrawText(TextFormat("Time Warp: %d steps/frame", timeWarp), 20, 45, 15, YELLOW);
            DrawText("- Drag L-Click: Free Slingshot", 20, 70, 15, WHITE);
            DrawText("- SHIFT + L-Click: Orbit Target", 20, 95, 15, GREEN);
            
            const char* targetName = (focusIdx >= 0 && focusIdx < numBodies) ? system[focusIdx].name : "SUN (Default)";
            DrawText(TextFormat("TARGET: %s", targetName), 20, 120, 15, SKYBLUE);
            DrawText(TextFormat("Bodies: %d/%d", numBodies, MAX_BODIES), 250, 120, 15, LIGHTGRAY);

        EndDrawing();
    }
    CloseWindow();
    return 0;
}