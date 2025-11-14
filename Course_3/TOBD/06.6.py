
import requests
from pathlib import Path
from tqdm import tqdm
import time
import multiprocessing
import os

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


ROOT_IMGS_DIR_PROCESSES = Path("imgs_processes")

def download_product_imgs_processes(args):
    """
    Создает папку для товара, скачивает в нее все изображения
    и выводит ID текущего процесса.
    Принимает кортеж (title, img_urls) для совместимости с pool.map.
    """
    title, img_urls = args

    # Выводим ID процесса
    process_id = multiprocessing.current_process().pid
    print(f"Process ID: {process_id} | Скачиваю изображения для '{title}'")

    # Создаем папку для конкретного товара
    product_dir = ROOT_IMGS_DIR_PROCESSES / title
    product_dir.mkdir(exist_ok=True, parents=True)

    for url in img_urls:
        try:
            img_content = requests.get(url).content
            file_name = Path(url).name
            save_path = product_dir / file_name
            with open(save_path, "wb") as f:
                f.write(img_content)
        except requests.exceptions.RequestException as e:
            print(f"Process ID: {process_id} | Не удалось скачать {url}: {e}")


if __name__ == '__main__':
    # Создаем корневую директорию
    ROOT_IMGS_DIR_PROCESSES.mkdir(exist_ok=True)

    print("Начинаю параллельное скачивание изображений с помощью процессов...")
    start_time = time.time()

    tasks = list(products_dict.items())

    num_processes = os.cpu_count() or 2
    print(f"Используется {num_processes} процессов.")

    with multiprocessing.Pool(processes=num_processes) as pool:
        list(tqdm(pool.imap(download_product_imgs_processes, tasks), total=len(tasks), desc="Скачивание (процессы)"))

    end_time = time.time()
    print("\nСкачивание завершено.")
    print(f"Время выполнения: {end_time - start_time:.4f} секунд")

    total_files = sum(1 for path in ROOT_IMGS_DIR_PROCESSES.rglob('*') if path.is_file())
    print(f"\nОбщее количество загруженных файлов: {total_files}")
