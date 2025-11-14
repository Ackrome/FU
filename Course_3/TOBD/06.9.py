
import numpy as np
import time
import os
import multiprocessing
from multiprocessing.pool import ThreadPool

# --- Шаг 1: Определение функций для NumPy ---

def create_2d_arr(m: int, n: int) -> np.ndarray:
    """
    Создает матрицу m x n в виде массива numpy,
    заполненную числами из стандартного нормального распределения.
    """
    return np.random.randn(m, n)

def sum_by_chunk_np(chunk: np.ndarray) -> float:
    """
    Принимает часть матрицы (массив numpy) и возвращает сумму ее элементов,
    используя np.sum().
    """
    return np.sum(chunk)

# --- Шаг 2: Основной блок выполнения ---

# Обязательная конструкция для использования multiprocessing
if __name__ == '__main__':
    # Задаем параметры
    M = 200_000  # Количество строк
    N = 100      # Количество столбцов
    CHUNK_SIZE = 1000 # Размер одной части для параллельной обработки

    print(f"Создается матрица {M}x{N} в виде массива numpy...")
    matrix_np = create_2d_arr(M, N)
    print("Матрица создана.\n")

    # --- 1. Последовательное выполнение (Numpy) ---
    print("--- 1. Последовательное выполнение (Numpy) ---")
    start_time_seq = time.time()

    total_sum_seq = sum_by_chunk_np(matrix_np)

    end_time_seq = time.time()
    print(f"Сумма элементов: {total_sum_seq:.4f}")
    print(f"Время выполнения: {end_time_seq - start_time_seq:.4f} секунд\n")

    # --- 2. Параллельное выполнение с процессами (Numpy) ---
    print("--- 2. Параллельное выполнение с процессами (Numpy) ---")
    start_time_proc = time.time()

    # Разбиваем массив numpy на части
    chunks = [matrix_np[i:i + CHUNK_SIZE] for i in range(0, M, CHUNK_SIZE)]

    num_processes = os.cpu_count() or 2
    print(f"Используется {num_processes} процессов...")

    with multiprocessing.Pool(processes=num_processes) as pool:
        results_proc = pool.map(sum_by_chunk_np, chunks)

    total_sum_proc = sum(results_proc)

    end_time_proc = time.time()
    print(f"Сумма элементов: {total_sum_proc:.4f}")
    print(f"Время выполнения: {end_time_proc - start_time_proc:.4f} секунд\n")

    # --- 3. Параллельное выполнение с потоками (Numpy) ---
    print("--- 3. Параллельное выполнение с потоками (Numpy) ---")
    start_time_thread = time.time()

    # chunks у нас уже есть
    num_threads = os.cpu_count() or 2
    print(f"Используется {num_threads} потоков...")

    with ThreadPool(processes=num_threads) as pool:
        results_thread = pool.map(sum_by_chunk_np, chunks)

    total_sum_thread = sum(results_thread)

    end_time_thread = time.time()
    print(f"Сумма элементов: {total_sum_thread:.4f}")
    print(f"Время выполнения: {end_time_thread - start_time_thread:.4f} секунд\n")
