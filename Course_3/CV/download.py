import asyncio
import aiohttp
from PIL import Image
from io import BytesIO
from pathlib import Path

# --- Конфигурация ---
BASE_URL = "https://gigarama.ru/velofest-open2026/xml/panos/P0020690.tiles/l{l}/{v:02d}/l{l}_{v:02d}_{h:02d}.jpg"
LEVEL = 6  # Высший уровень детализации из multires
WIDTH = 14336
HEIGHT = 10752
TILE_SIZE = 512

# Высчитываем количество столбцов и строк
COLS = (WIDTH + TILE_SIZE - 1) // TILE_SIZE
ROWS = (HEIGHT + TILE_SIZE - 1) // TILE_SIZE

# Лимит одновременных соединений, чтобы не улететь в бан
CONCURRENCY_LIMIT = 20 

async def fetch_tile(session: aiohttp.ClientSession, sem: asyncio.Semaphore, l: int, v: int, h: int) -> tuple:
    """Скачивает один тайл и возвращает его вместе с координатами."""
    url = BASE_URL.format(l=l, v=v, h=h)
    
    async with sem:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                return (v, h, data)
            else:
                print(f"Ошибка {response.status} при скачивании {url}")
                return (v, h, None)

async def main():
    print(f"Ожидается скачивание {COLS * ROWS} тайлов...")
    
    # Создаем холст для итогового изображения в памяти
    canvas = Image.new('RGB', (WIDTH, HEIGHT))
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    tasks = []
    async with aiohttp.ClientSession() as session:
        # krpano по умолчанию использует 1-based индексы
        for v in range(1, ROWS + 1):
            for h in range(1, COLS + 1):
                tasks.append(fetch_tile(session, sem, LEVEL, v, h))
        
        # Запускаем загрузку
        for future in asyncio.as_completed(tasks):
            v, h, data = await future
            if data:
                try:
                    # Конвертируем байты в картинку
                    img = Image.open(BytesIO(data))
                    
                    # Координаты для вставки (учитываем, что индексы с 1)
                    x = (h - 1) * TILE_SIZE
                    y = (v - 1) * TILE_SIZE
                    
                    # Вклеиваем на холст
                    canvas.paste(img, (x, y))
                except Exception as e:
                    print(f"Ошибка при обработке тайла v:{v} h:{h} - {e}")

    # Сохраняем результат
    output_path = Path("velofest_result.jpg")
    print(f"Сохранение файла {output_path}...")
    canvas.save(output_path, quality=95)
    print("Готово!")

if __name__ == "__main__":
    asyncio.run(main())