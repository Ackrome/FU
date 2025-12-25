import os
import shutil
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm.auto import tqdm
from pathlib import Path

# ================= КОНФИГУРАЦИЯ =================
DATA_FOLDER = Path('data') /'yummi-classification-fu25'
TRUE_TEST_PATH = DATA_FOLDER / 'test'
TRAIN_PATH = DATA_FOLDER / 'train'
VAL_PATH = DATA_FOLDER / "val"
CHECKPOINTS_KR = Path('checkpoints')
SOURCE_DIR = TRAIN_PATH  # Где сейчас лежат папки gyoza, manti...
CLEAN_DIR =  DATA_FOLDER / 'clean' # Куда сохранять чистые
TRASH_DIR = DATA_FOLDER / 'trash_bin'     # Куда кидать мусор (для проверки)

# Насколько модель должна быть уверена, что это НЕ еда, чтобы выкинуть (0.5 = 50%)
TRASH_THRESHOLD = 0.6 

# Текстовые промпты для CLIP
# Мы сравниваем "food" против всего остального
POS_PROMPT = "a photo of food, dumplings, meat, or dough"
NEG_PROMPTS = [
    "a photo of a person", 
    "a photo of an empty plate", 
    "a photo of a cat or dog",
    "a photo of text or document",
    "a blurred image",
    "a photo of random object",
    "noise"
]
ALL_LABELS = [POS_PROMPT] + NEG_PROMPTS
# ===============================================

def clean_data():
    # 1. Загружаем CLIP (Маленькая и быстрая версия)
    print("🤖 Loading CLIP model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Создаем папки
    if os.path.exists(CLEAN_DIR): shutil.rmtree(CLEAN_DIR)
    if os.path.exists(TRASH_DIR): shutil.rmtree(TRASH_DIR)
    
    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs(TRASH_DIR, exist_ok=True)

    # 2. Сканируем файлы
    file_list = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_list.append(os.path.join(root, file))

    print(f"🔍 Found {len(file_list)} images. Starting scanning...")

    # 3. Процесс фильтрации
    # Обрабатываем по одной (можно батчами для ускорения, но так надежнее для скрипта)
    kept_count = 0
    trash_count = 0

    with torch.no_grad():
        for file_path in tqdm(file_list):
            try:
                image = Image.open(file_path).convert("RGB")
                
                # Готовим данные для CLIP
                inputs = processor(
                    text=ALL_LABELS, 
                    images=image, 
                    return_tensors="pt", 
                    padding=True
                ).to(device)

                # Прогоняем через модель
                outputs = model(**inputs)
                
                # Считаем вероятности (Softmax)
                logits_per_image = outputs.logits_per_image # similarity score
                probs = logits_per_image.softmax(dim=1) # [1, len(ALL_LABELS)]

                # Индекс 0 - это POS_PROMPT ("food"), остальные - NEG
                prob_food = probs[0, 0].item()
                prob_trash = 1.0 - prob_food # Сумма вероятностей мусора

                # Определяем папку назначения
                # Сохраняем структуру классов (gyoza/img.jpg)
                rel_path = os.path.relpath(file_path, SOURCE_DIR)
                
                if prob_trash > TRASH_THRESHOLD:
                    # Это мусор
                    dest_path = os.path.join(TRASH_DIR, rel_path)
                    trash_count += 1
                else:
                    # Это еда
                    dest_path = os.path.join(CLEAN_DIR, rel_path)
                    kept_count += 1

                # Копируем
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"\n✅ Done!")
    print(f"🥗 Kept (Clean): {kept_count}")
    print(f"🗑️ Removed (Trash): {trash_count}")
    print(f"Trash files are in {TRASH_DIR} - check them visually!")

# Запуск
clean_data()