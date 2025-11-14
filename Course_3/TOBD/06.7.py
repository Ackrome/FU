
import requests
from pathlib import Path
from tqdm import tqdm
import time
import os
import threading
from multiprocessing.pool import ThreadPool 

url = "https://dummyjson.com/products?limit=50&skip=0"
products_dict = {}
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if 'products' in data:
        for product in data['products']:
            title = product.get('title')
            images = product.get('images', [])
            if title and images:
                formatted_title = title.replace('/', ' ')
                products_dict[formatted_title] = images
except requests.exceptions.RequestException as e:
    print(f"Не удалось получить данные о продуктах: {e}")
    exit()


ROOT_IMGS_DIR_THREADS = Path("imgs_threads")

def download_product_imgs_threads(args):
    """
    Создает папку для товара, скачивает в нее все изображения
    и выводит ID текущего процесса и потока.
    Принимает кортеж (title, img_urls) для совместимости с pool.map.
    """
    title, img_urls = args

    # Получаем ID процесса и потока
    process_id = os.getpid() # os.getpid() - простой способ получить ID процесса
    thread_id = threading.get_ident()

    # Выводим ID процесса и потока
    print(f"Process ID: {process_id} Thread ID: {thread_id} | Скачиваю изображения для '{title}'")

    # Создаем папку для конкретного товара
    product_dir = ROOT_IMGS_DIR_THREADS / title
    product_dir.mkdir(exist_ok=True, parents=True)

    for url in img_urls:
        try:
            img_content = requests.get(url).content
            file_name = Path(url).name
            save_path = product_dir / file_name
            with open(save_path, "wb") as f:
                f.write(img_content)
        except requests.exceptions.RequestException as e:
            print(f"Process ID: {process_id} Thread ID: {thread_id} | Не удалось скачать {url}: {e}")

# --- Шаг 3: Параллельное скачивание с использованием ThreadPool ---

# Создаем корневую директорию
ROOT_IMGS_DIR_THREADS.mkdir(exist_ok=True)

print("Начинаю параллельное скачивание изображений с помощью потоков...")
start_time = time.time()

# Подготавливаем список задач для пула потоков
tasks = list(products_dict.items())

# Определяем количество потоков (для I/O-задач можно использовать больше потоков, чем ядер)
num_threads = os.cpu_count() or 2
print(f"Используется {num_threads} потоков.")

# Создаем пул потоков и распределяем задачи
# Интерфейс ThreadPool идентичен Pool
with ThreadPool(processes=num_threads) as pool:
    # Используем pool.imap для совместимости с tqdm
    list(tqdm(pool.imap(download_product_imgs_threads, tasks), total=len(tasks), desc="Скачивание (потоки)"))

end_time = time.time()
print("\nСкачивание завершено.")
print(f"Время выполнения: {end_time - start_time:.4f} секунд")

# --- Шаг 4: Подсчет общего количества загруженных файлов ---
total_files = sum(1 for path in ROOT_IMGS_DIR_THREADS.rglob('*') if path.is_file())
print(f"\nОбщее количество загруженных файлов: {total_files}")
