import os
from pathlib import Path
from typing import List, Dict, Tuple
from multiprocessing import Pool, cpu_count

import imagehash
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from tqdm.auto import tqdm  # Используем tqdm для ноутбуков

class DatasetCleaner:
    def __init__(self, root_dir: str, hash_size: int = 8, threshold: int = 0):
        self.root_dir = Path(root_dir)
        self.hash_size = hash_size
        self.threshold = threshold
        self.extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

    def _compute_hash_and_info(self, file_path: Path) -> Tuple[str, Path, int]:
        try:
            with Image.open(file_path) as img:
                img_hash = imagehash.phash(img, hash_size=self.hash_size)
                width, height = img.size
                return str(img_hash), file_path, width * height
        except Exception:
            return None, file_path, -1

    def find_duplicates(self) -> Dict[str, List[Tuple[Path, int]]]:
        all_files = [p for p in self.root_dir.rglob('*') if p.suffix.lower() in self.extensions]
        print(f"🔍 Сканирую {len(all_files)} изображений...")

        with Pool(processes=cpu_count()) as pool:
            results = list(tqdm(pool.imap(self._compute_hash_and_info, all_files), total=len(all_files)))

        hashes_dict = {}
        for h_str, path, area in results:
            if h_str:
                hashes_dict.setdefault(h_str, []).append((path, area))

        # Оставляем только те, где больше 1 картинки
        return {k: v for k, v in hashes_dict.items() if len(v) > 1}

    def inspect_duplicates(self, num_samples: int = 5):
        """
        Визуализирует пары: [ОСТАВЛЯЕМ] vs [УДАЛЯЕМ].
        """
        duplicates = self.find_duplicates()
        
        if not duplicates:
            print("✅ Дубликатов нет.")
            return

        print(f"⚠️ Найдено групп дубликатов: {len(duplicates)}")
        print(f"👀 Показываю первые {num_samples} примеров для проверки...\n")

        # Берем первые N групп для визуализации
        sample_keys = list(duplicates.keys())[:num_samples]

        for h_str in sample_keys:
            file_list = duplicates[h_str]
            # Сортировка: Самое большое разрешение -> index 0 (Оставляем)
            file_list.sort(key=lambda x: x[1], reverse=True)
            
            keep_file, keep_area = file_list[0]
            # Берем первый из кандидатов на удаление для примера
            del_file, del_area = file_list[1] 

            self._plot_comparison(keep_file, keep_area, del_file, del_area)

    def _plot_comparison(self, keep_path, keep_area, del_path, del_area):
        """Рисует два изображения рядом"""
        try:
            fig, axes = plt.subplots(1, 2, figsize=(10, 5))
            
            # Картинка, которую оставляем
            img_keep = Image.open(keep_path)
            axes[0].imshow(img_keep)
            axes[0].set_title(f"✅ KEEP (Higher Res)\n{keep_path.name}\nArea: {keep_area} px", color='green', fontweight='bold')
            axes[0].axis('off')

            # Картинка, которую удаляем
            img_del = Image.open(del_path)
            axes[1].imshow(img_del)
            axes[1].set_title(f"❌ DELETE (Duplicate)\n{del_path.name}\nArea: {del_area} px", color='red', fontweight='bold')
            axes[1].axis('off')

            plt.tight_layout()
            plt.show()
            
            # Закрываем файлы явно
            img_keep.close()
            img_del.close()
            
        except Exception as e:
            print(f"Ошибка при отображении: {e}")

    def delete_duplicates(self):
        """
        РЕАЛЬНОЕ УДАЛЕНИЕ. Запускать только после проверки!
        """
        duplicates = self.find_duplicates()
        deleted_count = 0
        
        for file_list in tqdm(duplicates.values(), desc="Deleting"):
            file_list.sort(key=lambda x: x[1], reverse=True)
            # Все кроме первого (нулевого индекса) удаляем
            for rm_file, _ in file_list[1:]:
                try:
                    os.remove(rm_file)
                    deleted_count += 1
                except OSError as e:
                    print(f"Error: {e}")
        
        print(f"🔥 УДАЛЕНО файлов: {deleted_count}")

# --- Использование ---
# 1. Инициализация
cleaner = DatasetCleaner(root_dir=r'C:\Projects\FU\Course_3\DL\data\yummi-classification-fu25\train\gyoza')

# 2. СМОТРИМ ГЛАЗАМИ (Безопасно)
# Изменяй num_samples, чтобы посмотреть больше пар
cleaner.inspect_duplicates(num_samples=5)