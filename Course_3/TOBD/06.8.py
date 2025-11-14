
import numpy as np
import time
import os
import multiprocessing
from multiprocessing.pool import ThreadPool

# --- Шаг 1: Определение функций ---

def create_2d_list(m: int, n: int) -> list[list[float]]:
    """
    Создает матрицу m x n в виде списка списков,
    заполненную числами из стандартного нормального распределения.
    """
    # Используем numpy для быстрой генерации, затем конвертируем в list of lists
    return np.random.randn(m, n).tolist()

def sum_by_chunk(chunk: list[list[float]]) -> float:
    """
    Принимает часть матрицы (список списков) и возвращает сумму ее элементов.
    Использует стандартные средства Python, без numpy.
    """
    # Используем генераторное выражение для эффективности и краткости
    return sum(item for row in chunk for item in row)

# --- Шаг 2: Основной блок выполнения ---

# Обязательная конструкция для использования multiprocessing
if __name__ == '__main__':
    # Задаем параметры
    M = 200_000  # Количество строк
    N = 100      # Количество столбцов
    CHUNK_SIZE = 1000 # Размер одной части для параллельной обработки

    print(f"Создается матрица {M}x{N} в виде списка списков...")
    matrix = create_2d_list(M, N)
    print("Матрица создана.\n")

    # --- 1. Последовательное выполнение ---
    print("--- 1. Последовательное выполнение ---")
    start_time_seq = time.time()

    total_sum_seq = sum_by_chunk(matrix)

    end_time_seq = time.time()
    print(f"Сумма элементов: {total_sum_seq:.4f}")
    print(f"Время выполнения: {end_time_seq - start_time_seq:.4f} секунд\n")

    # --- 2. Параллельное выполнение с процессами ---
    print("--- 2. Параллельное выполнение с процессами ---")
    start_time_proc = time.time()

    # Разбиваем матрицу на части
    chunks = [matrix[i:i + CHUNK_SIZE] for i in range(0, M, CHUNK_SIZE)]

    num_processes = os.cpu_count() or 2
    print(f"Используется {num_processes} процессов...")

    with multiprocessing.Pool(processes=num_processes) as pool:
        # Распределяем chunks по процессам и применяем функцию sum_by_chunk
        results_proc = pool.map(sum_by_chunk, chunks)

    # Агрегируем результаты
    total_sum_proc = sum(results_proc)

    end_time_proc = time.time()
    print(f"Сумма элементов: {total_sum_proc:.4f}")
    print(f"Время выполнения: {end_time_proc - start_time_proc:.4f} секунд\n")

    # --- 3. Параллельное выполнение с потоками ---
    print("--- 3. Параллельное выполнение с потоками ---")
    start_time_thread = time.time()

    # chunks у нас уже есть из предыдущего шага
    num_threads = os.cpu_count() or 2
    print(f"Используется {num_threads} потоков...")

    with ThreadPool(processes=num_threads) as pool:
        # Распределяем chunks по потокам
        results_thread = pool.map(sum_by_chunk, chunks)

    # Агрегируем результаты
    total_sum_thread = sum(results_thread)

    end_time_thread = time.time()
    print(f"Сумма элементов: {total_sum_thread:.4f}")
    print(f"Время выполнения: {end_time_thread - start_time_thread:.4f} секунд\n")
