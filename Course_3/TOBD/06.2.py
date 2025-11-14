
import pandas as pd
import re
import time
import numpy as np
from multiprocessing import Pool
import os
from functools import partial

def f(tag: str) -> bool:
    """
    Проверяет, удовлетворяет ли тэг шаблону: [любое число]-[любое слово]-or-less.
    """
    if not isinstance(tag, str):
        return False
    pattern = r'^\d+-[a-zA-Z]+-or-less$'
    return bool(re.fullmatch(pattern, tag))

def _map_on_chunk(chunk: pd.Series, func: callable) -> pd.Series:
    """Вспомогательная функция для применения .map() к части данных."""
    return chunk.map(func)

def parallel_map(s: pd.Series, f: callable) -> pd.Series:
    """
    Применяет функцию f к серии s, распараллеливая вычисления
    на K процессов, где K - количество ядер CPU.
    """
    cpu_cores = os.cpu_count()
    if cpu_cores is None:
        cpu_cores = 2
    print(f"Используется {cpu_cores} ядер процессора.")

    chunks = np.array_split(s, cpu_cores)

    worker_func = partial(_map_on_chunk, func=f)

    with Pool(cpu_cores) as pool:
        processed_chunks = pool.map(worker_func, chunks)

    result_series = pd.concat(processed_chunks)

    return result_series

if __name__ == '__main__':
    start_time = time.time()

    df = pd.read_csv('\\'.join(__file__.split('\\')[:-1])+'\\data\\tag_nsteps_10m.csv')

    matching_series = parallel_map(df['tags'], f)

    matching_count = matching_series.sum()

    print(f"Количество подходящих тегов: {matching_count}")

    end_time = time.time()

    print(f"Время выполнения: {end_time - start_time:.4f} секунд")
