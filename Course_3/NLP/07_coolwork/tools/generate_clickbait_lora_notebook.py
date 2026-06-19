from __future__ import annotations

import json
from pathlib import Path


NOTEBOOK_PATH = Path("llm_lora_clickbait_kaggle.ipynb")


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip().splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip("\n").splitlines(keepends=True),
    }


cells = [
    md(
        """
# LLM + QLoRA для бинарной классификации кликбейтных заголовков

В этом ноутбуке решается лабораторная задача по NLP: маленькая LLM дообучается через LoRA/QLoRA для классификации новостных заголовков на два класса.

Модель получает инструкционный промпт и должна сгенерировать ровно одну метку:

- `A` = `not_clickbait`
- `B` = `clickbait`

Подход использует SFT-формат для causal language modeling: промпт и целевой ответ объединяются, а токены промпта маскируются в `labels` значением `-100`, чтобы loss считался только по ответу.

В конце ноутбук сохраняет адаптер LoRA, предсказания, метрики, графики и HTML-отчет в `/kaggle/working`.
"""
    ),
    md(
        """
## Установка зависимостей

На Kaggle часть библиотек уже может быть установлена, но версии часто отличаются. Эта ячейка обновляет стек Hugging Face, PEFT, bitsandbytes и библиотеки для метрик/визуализации.

`wandb` отключен в конфигурации ниже, поэтому логин в сторонние сервисы не требуется.
"""
    ),
    code(
        """
!pip -q install -U "transformers>=4.45.0" "datasets>=2.20.0" "accelerate>=0.33.0" "peft>=0.12.0" "bitsandbytes>=0.43.3" "scikit-learn>=1.3.0" "matplotlib>=3.7.0" "seaborn>=0.13.0" "pandas>=2.0.0"
"""
    ),
    md(
        """
## Импорты и глобальная конфигурация

Главные переключатели находятся в этой ячейке. Для смены модели достаточно изменить `MODEL_NAME`; запасные модели перечислены в `FALLBACK_MODEL_NAMES`.

Для быстрой проверки пайплайна можно включить `FAST_DEV_RUN=True`: тогда будут взяты маленькие подвыборки train/val/test.
"""
    ),
    code(
        r'''
import gc
import html
import inspect
import json
import math
import os
import random
import re
import time
import unicodedata
import warnings
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from datasets import Dataset, DatasetDict
from IPython.display import HTML, Markdown, display
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)

try:
    import seaborn as sns
except Exception:
    sns = None

warnings.filterwarnings("ignore")
os.environ["WANDB_DISABLED"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# -----------------------------
# Main experiment configuration
# -----------------------------
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
FALLBACK_MODEL_NAMES = ["Qwen/Qwen3-1.7B", "Qwen/Qwen3-2B"]
TRY_FALLBACK_MODELS = False  # Set True if the primary model is unavailable.

SEED = 42
MAX_LENGTH = 160
NUM_TRAIN_EPOCHS = 2
LEARNING_RATE = 2e-4
PER_DEVICE_TRAIN_BATCH_SIZE = 4
PER_DEVICE_EVAL_BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 8
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LOGGING_STEPS = 25
SAVE_TOTAL_LIMIT = 2

FAST_DEV_RUN = False
ZERO_SHOT_N = 300
TRAIN_N = None  # Example: 5000. Leave None to use the full train split.
USE_FIXED_32000_SPLIT = True
TEAM_SPLIT_DATASET_DIR = Path("/kaggle/input/datasets/kvdep1/clickbait-dataset-split")
LEAKAGE_POLICY = "raise"  # "raise" or "drop_eval_duplicates"
CONFLICT_POLICY = "drop"  # Canonical duplicate headlines with conflicting labels.
BEST_MODEL_METRIC = "eval_ab_f1"
FINAL_TRAIN_ON_TRAIN_VAL = True
TRAIN_VAL_EVAL_N = None  # Keep None for full train+val metrics; use an int for a faster report.

GENERATION_BATCH_SIZE = 8
MAX_NEW_TOKENS = 4

TEXT_COL_CANDIDATES = ["headline", "text", "title", "content"]
LABEL_COL_CANDIDATES = ["clickbait", "label", "class", "target"]
SPLIT_COL_CANDIDATES = ["split", "set", "subset", "data_split"]

RNN_BENCHMARK = {
    "train_accuracy": 0.9929,
    "train_f1": 0.9929,
    "val_accuracy": 0.9744,
    "val_f1": 0.9742,
    "test_accuracy": 0.9612,
    "test_f1": 0.9610,
    "train_size": 28800,
    "val_size": 1600,
    "test_size": 1600,
}

KAGGLE_INPUT_DIR = Path("/kaggle/input")
KAGGLE_WORKING_DIR = Path("/kaggle/working")
if not KAGGLE_INPUT_DIR.exists():
    # Local fallback for syntax checks or dry runs outside Kaggle.
    KAGGLE_INPUT_DIR = Path("data")

OUTPUT_DIR = KAGGLE_WORKING_DIR if KAGGLE_WORKING_DIR.exists() else Path("kaggle_working")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_CANDIDATES = [MODEL_NAME] + (FALLBACK_MODEL_NAMES if TRY_FALLBACK_MODELS else [])
print("Model candidates:", MODEL_CANDIDATES)
print("Preferred pre-split dataset directory:", TEAM_SPLIT_DATASET_DIR)
print("Input directory:", KAGGLE_INPUT_DIR.resolve() if KAGGLE_INPUT_DIR.exists() else KAGGLE_INPUT_DIR)
print("Output directory:", OUTPUT_DIR.resolve())
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    for idx in range(torch.cuda.device_count()):
        print(f"GPU {idx}: {torch.cuda.get_device_name(idx)}")
else:
    print("Warning: 4-bit bitsandbytes training is intended for CUDA GPUs.")
'''
    ),
    md(
        """
## Воспроизводимость

Фиксируем seed для Python, NumPy, PyTorch и CUDA. Это не делает обучение полностью детерминированным на GPU, но уменьшает разброс между запусками.
"""
    ),
    code(
        """
def set_global_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def clear_cuda_cache() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


set_global_seed(SEED)
clear_cuda_cache()
"""
    ),
    md(
        """
## Загрузка датасета и поиск CSV

Датасет команды должен быть подключен как Kaggle input по пути `/kaggle/input/datasets/kvdep1/clickbait-dataset-split`. Внутри ожидаются заранее подготовленные файлы `train.csv`, `val.csv` и `test.csv`.

Код сначала использует эти готовые split-файлы как авторитетное разбиение команды. Если они не найдены, остается fallback на рекурсивный поиск одного CSV внутри `/kaggle/input`, чтобы ноутбук можно было локально проверить на другой копии датасета.
"""
    ),
    code(
        r'''
def normalize_column_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def read_csv_robust(path: Path, nrows: int | None = None) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin1"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding, nrows=nrows, low_memory=False)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Cannot read CSV file {path}: {last_error}")


def score_csv_candidate(path: Path) -> dict[str, Any]:
    try:
        sample = read_csv_robust(path, nrows=1000)
    except Exception as exc:
        return {"path": path, "score": -1, "error": repr(exc), "columns": []}

    normalized_cols = [normalize_column_name(c) for c in sample.columns]
    text_score = sum(4 for c in normalized_cols if c in TEXT_COL_CANDIDATES)
    label_score = sum(4 for c in normalized_cols if c in LABEL_COL_CANDIDATES)
    binary_score = 0
    for col in sample.columns:
        nunique = sample[col].dropna().nunique()
        if 1 < nunique <= 10:
            binary_score += 1
    row_score = min(len(sample) / 1000, 1.0)
    total = text_score + label_score + binary_score + row_score
    return {
        "path": path,
        "score": total,
        "rows_sampled": len(sample),
        "columns": list(sample.columns),
        "error": None,
    }


SPLIT_FILE_CANDIDATES = {
    "train": ["train.csv", "training.csv"],
    "validation": ["val.csv", "valid.csv", "validation.csv"],
    "test": ["test.csv"],
}


def find_file_case_insensitive(directory: Path, names: list[str]) -> Path | None:
    if not directory.exists() or not directory.is_dir():
        return None
    lookup = {item.name.lower(): item for item in directory.iterdir() if item.is_file()}
    for name in names:
        match = lookup.get(name.lower())
        if match is not None:
            return match
    return None


def split_csv_paths_in_dir(directory: Path) -> dict[str, Path] | None:
    paths: dict[str, Path] = {}
    for split_name, names in SPLIT_FILE_CANDIDATES.items():
        match = find_file_case_insensitive(directory, names)
        if match is None:
            return None
        paths[split_name] = match
    return paths


def find_presplit_csv_paths(preferred_dir: Path, search_root: Path) -> tuple[dict[str, Path], Path] | None:
    preferred_paths = split_csv_paths_in_dir(preferred_dir)
    if preferred_paths is not None:
        return preferred_paths, preferred_dir

    if search_root.exists():
        for train_file in sorted(search_root.rglob("train.csv")):
            candidate_dir = train_file.parent
            candidate_paths = split_csv_paths_in_dir(candidate_dir)
            if candidate_paths is not None:
                return candidate_paths, candidate_dir
    return None


def find_best_csv(root: Path) -> Path:
    csv_files = sorted(root.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files were found in {root}. Attach the Kaggle dataset first."
        )

    scores = [score_csv_candidate(path) for path in csv_files]
    score_df = pd.DataFrame(
        [
            {
                "path": str(item["path"]),
                "score": item["score"],
                "rows_sampled": item.get("rows_sampled"),
                "columns": ", ".join(map(str, item.get("columns", [])))[:180],
                "error": item.get("error"),
            }
            for item in scores
        ]
    ).sort_values("score", ascending=False)
    display(score_df)

    best = max(scores, key=lambda item: item["score"])
    if best["score"] < 0:
        raise RuntimeError("CSV files were found, but none could be read.")
    return best["path"]


presplit_result = find_presplit_csv_paths(TEAM_SPLIT_DATASET_DIR, KAGGLE_INPUT_DIR)
if presplit_result is not None:
    split_csv_paths, presplit_dataset_dir = presplit_result
    csv_path = presplit_dataset_dir
    dataset_source = "pre_split_csvs"
    raw_parts = []
    split_rows = []
    for split_name, path in split_csv_paths.items():
        part = read_csv_robust(path)
        part["_source_split"] = split_name
        part["_source_file"] = str(path)
        raw_parts.append(part)
        split_rows.append({"split": split_name, "path": str(path), "rows": len(part)})
    raw_df = pd.concat(raw_parts, ignore_index=True)
    print("Using pre-split CSV files from:", presplit_dataset_dir)
    display(pd.DataFrame(split_rows))
else:
    print("Pre-split train/val/test CSV files were not found. Falling back to single-CSV detection.")
    split_csv_paths = {}
    presplit_dataset_dir = None
    dataset_source = "single_csv_fallback"
    csv_path = find_best_csv(KAGGLE_INPUT_DIR)
    print("Selected CSV:", csv_path)
    raw_df = read_csv_robust(csv_path)

print("Raw shape:", raw_df.shape)
display(raw_df.head())
'''
    ),
    md(
        """
## Предобработка датасета

Код автоматически определяет текстовую колонку и колонку метки. Поддерживаются типичные названия `headline`, `text`, `title`, `content` для текста и `clickbait`, `label`, `class`, `target` для меток.

Метки приводятся к бинарному виду:

- `0` = `not_clickbait` = ответ `A`
- `1` = `clickbait` = ответ `B`
"""
    ),
    code(
        r'''
def infer_text_column(df: pd.DataFrame) -> str:
    normalized = {
        col: normalize_column_name(col)
        for col in df.columns
        if not str(col).startswith("_")
    }

    for candidate in TEXT_COL_CANDIDATES:
        for col, norm in normalized.items():
            if norm == candidate:
                return col

    scored: list[tuple[float, str]] = []
    for col in df.columns:
        if str(col).startswith("_") or normalize_column_name(col) in SPLIT_COL_CANDIDATES:
            continue
        series = df[col].dropna().astype(str)
        if series.empty:
            continue
        avg_len = series.str.len().mean()
        unique_ratio = series.nunique() / max(len(series), 1)
        object_bonus = 2.0 if pd.api.types.is_object_dtype(df[col]) else 0.0
        name_bonus = 1.5 if any(token in normalized[col] for token in TEXT_COL_CANDIDATES) else 0.0
        score = avg_len * 0.05 + unique_ratio * 3 + object_bonus + name_bonus
        scored.append((score, col))

    if not scored:
        raise ValueError("Could not infer a text column.")
    return max(scored)[1]


def infer_label_column(df: pd.DataFrame, text_col: str) -> str:
    normalized = {
        col: normalize_column_name(col)
        for col in df.columns
        if col != text_col and not str(col).startswith("_")
    }

    for candidate in LABEL_COL_CANDIDATES:
        for col, norm in normalized.items():
            if norm == candidate:
                return col

    scored: list[tuple[float, str]] = []
    for col in df.columns:
        if col == text_col:
            continue
        if str(col).startswith("_") or normalize_column_name(col) in SPLIT_COL_CANDIDATES:
            continue
        series = df[col].dropna()
        if series.empty:
            continue
        nunique = series.nunique()
        if nunique < 2 or nunique > 20:
            continue
        norm = normalize_column_name(col)
        name_bonus = 4.0 if any(token in norm for token in LABEL_COL_CANDIDATES) else 0.0
        binary_bonus = 4.0 if nunique == 2 else 1.0
        compact_bonus = max(0.0, 2.0 - math.log10(nunique + 1))
        scored.append((name_bonus + binary_bonus + compact_bonus, col))

    if not scored:
        raise ValueError("Could not infer a label column.")
    return max(scored)[1]


def infer_split_column(df: pd.DataFrame) -> str | None:
    normalized = {col: normalize_column_name(col) for col in df.columns}
    for candidate in SPLIT_COL_CANDIDATES:
        for col, norm in normalized.items():
            if norm == candidate:
                values = set(df[col].dropna().astype(str).str.lower().str.strip().unique())
                if values & {"train", "training", "val", "valid", "validation", "test"}:
                    return col
    return None


def normalize_headline(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def canonical_headline_key(value: Any) -> str:
    text = unicodedata.normalize("NFKC", normalize_headline(value)).casefold()
    text = re.sub(r"https?://\S+|www\.\S+", " URL ", text)
    text = re.sub(r"[^0-9a-z]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_binary_label_mapping(series: pd.Series) -> dict[Any, int]:
    values = list(series.dropna().unique())
    if len(values) != 2:
        raise ValueError(f"Expected exactly two classes, found {len(values)}: {values[:20]}")

    def value_key(value: Any) -> str:
        return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")

    # Explicit mappings first.
    explicit_zero = {
        "0", "false", "no", "not_clickbait", "not_click_bait", "non_clickbait",
        "non_click_bait", "not", "regular", "normal", "news", "legitimate"
    }
    explicit_one = {
        "1", "true", "yes", "clickbait", "click_bait", "bait"
    }

    mapping: dict[Any, int] = {}
    for value in values:
        key = value_key(value)
        if key in explicit_zero or ("not" in key and "click" in key):
            mapping[value] = 0
        elif key in explicit_one or ("click" in key and "not" not in key and "non" not in key):
            mapping[value] = 1

    if len(mapping) == 2 and set(mapping.values()) == {0, 1}:
        return mapping

    # Numeric binary labels.
    numeric = pd.to_numeric(pd.Series(values), errors="coerce")
    if numeric.notna().all():
        sorted_values = [value for _, value in sorted(zip(numeric.tolist(), values))]
        return {sorted_values[0]: 0, sorted_values[1]: 1}

    # Last fallback: deterministic ordering, with a visible warning.
    sorted_values = sorted(values, key=lambda item: str(item).lower())
    print("Warning: label mapping was inferred by sorted order:", sorted_values)
    return {sorted_values[0]: 0, sorted_values[1]: 1}


text_col = infer_text_column(raw_df)
label_col = infer_label_column(raw_df, text_col)
split_col = infer_split_column(raw_df)
label_mapping = build_binary_label_mapping(raw_df[label_col])

print("Text column:", text_col)
print("Label column:", label_col)
print("Split column:", split_col)
print("Label mapping:", label_mapping)

df = raw_df.copy()
df["headline"] = df[text_col].map(normalize_headline)
df["label"] = df[label_col].map(label_mapping)
if "_source_split" in df.columns:
    df["_source_split"] = df["_source_split"].astype(str).str.lower().str.strip()
if split_col is not None:
    df["_original_split"] = df[split_col].astype(str).str.lower().str.strip()
df = df.dropna(subset=["headline", "label"]).copy()
df["label"] = df["label"].astype(int)
df = df[df["headline"].str.len() > 0].copy()
df["headline_key"] = df["headline"].map(canonical_headline_key)
df = df[df["headline_key"].str.len() > 0].copy()

conflicting_keys = (
    df.groupby("headline_key")["label"]
    .nunique()
    .loc[lambda s: s > 1]
    .index
)
conflict_count = int(len(conflicting_keys))
if conflict_count:
    conflict_examples = (
        df[df["headline_key"].isin(conflicting_keys)]
        .sort_values(["headline_key", "label"])
        [["headline", "headline_key", "label"]]
        .head(20)
    )
    display(conflict_examples)
    if CONFLICT_POLICY == "drop":
        df = df[~df["headline_key"].isin(conflicting_keys)].copy()
        print(f"Dropped {conflict_count} canonical headlines with conflicting labels.")
    else:
        raise ValueError(f"Found {conflict_count} canonical headlines with conflicting labels.")

dedup_subset = ["headline_key", "label"]
if "_source_split" in df.columns:
    dedup_subset = ["_source_split", "headline_key", "label"]
elif "_original_split" in df.columns:
    dedup_subset = ["_original_split", "headline_key", "label"]

duplicate_count_before = int(df.duplicated(subset=dedup_subset).sum())
df = df.drop_duplicates(subset=dedup_subset).reset_index(drop=True)
df["answer"] = np.where(df["label"].eq(1), "B", "A")
df["label_name"] = np.where(df["label"].eq(1), "clickbait", "not_clickbait")

print("Prepared shape:", df.shape)
print("Canonical duplicate rows removed:", duplicate_count_before)
print("Conflicting canonical headline keys:", conflict_count)
display(df[["headline", "label", "answer", "label_name"]].head())
display(df["label_name"].value_counts().rename_axis("class").reset_index(name="count"))
'''
    ),
    md(
        """
## Стратифицированное разбиение train/val/test

Сначала используется готовое командное разбиение из `train.csv`, `val.csv` и `test.csv`. Если оно недоступно, код пробует явную колонку split, затем фиксированное разбиение `28800/1600/1600` для датасета на 32 000 строк, и только потом fallback `90/5/5`.

Перед обучением выполняется проверка утечки: канонические ключи заголовков не должны пересекаться между train/val/test. По умолчанию `LEAKAGE_POLICY="raise"` останавливает запуск при пересечении.
"""
    ),
    code(
        r'''
def stratified_sample(frame: pd.DataFrame, n: int | None, seed: int = 42) -> pd.DataFrame:
    if n is None or n >= len(frame):
        return frame.reset_index(drop=True)
    if frame["label"].nunique() == 2 and n >= 2:
        sampled, _ = train_test_split(
            frame,
            train_size=n,
            random_state=seed,
            stratify=frame["label"],
        )
    else:
        sampled = frame.sample(n=n, random_state=seed)
    return sampled.reset_index(drop=True)


def split_from_source_files(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    if "_source_split" not in frame.columns:
        return None

    split_values = frame["_source_split"].map(
        {
            "train": "train",
            "training": "train",
            "val": "val",
            "valid": "val",
            "validation": "val",
            "dev": "val",
            "test": "test",
        }
    )
    train_df = frame[split_values.eq("train")].copy()
    val_df = frame[split_values.eq("val")].copy()
    test_df = frame[split_values.eq("test")].copy()

    if len(train_df) == 0 or len(val_df) == 0 or len(test_df) == 0:
        return None
    return train_df, val_df, test_df


def split_from_original_column(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    if "_original_split" not in frame.columns:
        return None

    split_values = frame["_original_split"].map(
        {
            "train": "train",
            "training": "train",
            "val": "val",
            "valid": "val",
            "validation": "val",
            "dev": "val",
            "test": "test",
        }
    )
    if split_values.isna().all():
        return None

    train_df = frame[split_values.eq("train")].copy()
    val_df = frame[split_values.eq("val")].copy()
    test_df = frame[split_values.eq("test")].copy()

    if len(train_df) == 0 or len(test_df) == 0:
        return None

    if len(val_df) == 0:
        train_df, val_df = train_test_split(
            train_df,
            test_size=0.05,
            random_state=SEED,
            stratify=train_df["label"],
        )
    return train_df, val_df, test_df


def make_train_val_test(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_files = split_from_source_files(frame)
    if source_files is not None:
        print("Using team pre-split train/val/test CSV files.")
        return source_files

    original = split_from_original_column(frame)
    if original is not None:
        print("Using original dataset split column.")
        return original

    if USE_FIXED_32000_SPLIT and len(frame) == 32000:
        train_df, temp_df = train_test_split(
            frame,
            train_size=28800,
            random_state=SEED,
            stratify=frame["label"],
        )
        val_df, test_df = train_test_split(
            temp_df,
            train_size=1600,
            random_state=SEED,
            stratify=temp_df["label"],
        )
        print("Using fixed 28800/1600/1600 split.")
        return train_df, val_df, test_df

    train_df, temp_df = train_test_split(
        frame,
        test_size=0.10,
        random_state=SEED,
        stratify=frame["label"],
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=SEED,
        stratify=temp_df["label"],
    )
    print("Using default 90/5/5 split.")
    return train_df, val_df, test_df


def split_overlap_table(train_frame: pd.DataFrame, val_frame: pd.DataFrame, test_frame: pd.DataFrame) -> pd.DataFrame:
    split_frames = {
        "train": train_frame,
        "val": val_frame,
        "test": test_frame,
    }
    rows = []
    pairs = [("train", "val"), ("train", "test"), ("val", "test")]
    for left_name, right_name in pairs:
        left_keys = set(split_frames[left_name]["headline_key"])
        right_keys = set(split_frames[right_name]["headline_key"])
        overlap = sorted(left_keys & right_keys)
        for key in overlap:
            left_example = split_frames[left_name].loc[
                split_frames[left_name]["headline_key"].eq(key), "headline"
            ].iloc[0]
            right_example = split_frames[right_name].loc[
                split_frames[right_name]["headline_key"].eq(key), "headline"
            ].iloc[0]
            rows.append(
                {
                    "left_split": left_name,
                    "right_split": right_name,
                    "headline_key": key,
                    "left_headline": left_example,
                    "right_headline": right_example,
                }
            )
    return pd.DataFrame(rows)


def enforce_no_split_leakage(
    train_frame: pd.DataFrame,
    val_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overlaps = split_overlap_table(train_frame, val_frame, test_frame)
    if overlaps.empty:
        print("Leakage check passed: no canonical headline overlap across train/val/test.")
        return train_frame, val_frame, test_frame, overlaps

    display(overlaps.head(30))
    message = f"Found {len(overlaps)} canonical headline overlaps across splits."
    if LEAKAGE_POLICY == "drop_eval_duplicates":
        train_keys = set(train_frame["headline_key"])
        val_frame = val_frame[~val_frame["headline_key"].isin(train_keys)].copy()
        blocked_test_keys = train_keys | set(val_frame["headline_key"])
        test_frame = test_frame[~test_frame["headline_key"].isin(blocked_test_keys)].copy()
        remaining = split_overlap_table(train_frame, val_frame, test_frame)
        if not remaining.empty:
            raise ValueError("Cross-split leakage remains after dropping eval duplicates.")
        print(message, "Dropped overlapping validation/test rows because LEAKAGE_POLICY='drop_eval_duplicates'.")
        return train_frame, val_frame, test_frame, overlaps

    raise ValueError(message + " Fix the split or set LEAKAGE_POLICY='drop_eval_duplicates'.")


train_df, val_df, test_df = make_train_val_test(df)
train_df = train_df.reset_index(drop=True)
val_df = val_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

train_df, val_df, test_df, leakage_overlaps_df = enforce_no_split_leakage(train_df, val_df, test_df)
train_df = train_df.reset_index(drop=True)
val_df = val_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

if TRAIN_N is not None:
    train_df = stratified_sample(train_df, TRAIN_N, SEED)

if FAST_DEV_RUN:
    train_df = stratified_sample(train_df, 1000, SEED)
    val_df = stratified_sample(val_df, 200, SEED)
    test_df = stratified_sample(test_df, 200, SEED)

train_val_df = pd.concat(
    [
        train_df.assign(source_eval_split="train"),
        val_df.assign(source_eval_split="val"),
    ],
    ignore_index=True,
).reset_index(drop=True)

dataset_info = {
    "dataset_source": dataset_source,
    "csv_path": str(csv_path),
    "split_csv_paths": {split: str(path) for split, path in split_csv_paths.items()},
    "text_column": text_col,
    "label_column": label_col,
    "split_column": split_col,
    "n_total_prepared": int(len(df)),
    "n_train": int(len(train_df)),
    "n_val": int(len(val_df)),
    "n_train_val": int(len(train_val_df)),
    "n_test": int(len(test_df)),
    "canonical_duplicate_rows_removed": duplicate_count_before,
    "conflicting_canonical_keys": conflict_count,
    "cross_split_overlap_examples": int(len(leakage_overlaps_df)),
    "leakage_policy": LEAKAGE_POLICY,
}
print(dataset_info)

split_summary = pd.DataFrame(
    [
        {"split": "train", "rows": len(train_df), "clickbait_rate": train_df["label"].mean()},
        {"split": "val", "rows": len(val_df), "clickbait_rate": val_df["label"].mean()},
        {"split": "test", "rows": len(test_df), "clickbait_rate": test_df["label"].mean()},
    ]
)
display(split_summary)

dataset = DatasetDict(
    {
        "train": Dataset.from_pandas(train_df[["headline", "label", "answer", "label_name"]], preserve_index=False),
        "validation": Dataset.from_pandas(val_df[["headline", "label", "answer", "label_name"]], preserve_index=False),
        "train_val": Dataset.from_pandas(train_val_df[["headline", "label", "answer", "label_name"]], preserve_index=False),
        "test": Dataset.from_pandas(test_df[["headline", "label", "answer", "label_name"]], preserve_index=False),
    }
)
dataset
'''
    ),
    md(
        """
## Разведочный анализ данных

Проверяем баланс классов, длины заголовков и несколько примеров из каждого класса. Это помогает заметить проблемы с колонками или разбиением до запуска дорогого обучения.
"""
    ),
    code(
        r'''
eda_df = pd.concat(
    [
        train_df.assign(split="train"),
        val_df.assign(split="val"),
        test_df.assign(split="test"),
    ],
    ignore_index=True,
)
eda_df["char_len"] = eda_df["headline"].str.len()
eda_df["word_len"] = eda_df["headline"].str.split().str.len()

class_distribution = (
    eda_df.groupby(["split", "label_name"])
    .size()
    .rename("count")
    .reset_index()
)
class_distribution["share"] = class_distribution.groupby("split")["count"].transform(lambda s: s / s.sum())
display(class_distribution)

length_stats = (
    eda_df.groupby("split")[["char_len", "word_len"]]
    .agg(["count", "mean", "median", "min", "max"])
    .round(2)
)
display(length_stats)

print("Examples from each class:")
for label_name in ["not_clickbait", "clickbait"]:
    display(
        eda_df[eda_df["label_name"].eq(label_name)][["headline", "label_name"]]
        .sample(min(5, (eda_df["label_name"] == label_name).sum()), random_state=SEED)
        .reset_index(drop=True)
    )

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
if sns is not None:
    sns.countplot(data=eda_df, x="split", hue="label_name", ax=axes[0])
    sns.histplot(data=eda_df, x="word_len", hue="label_name", bins=30, kde=False, ax=axes[1])
else:
    class_distribution.pivot(index="split", columns="label_name", values="count").plot(kind="bar", ax=axes[0])
    eda_df["word_len"].hist(bins=30, ax=axes[1])
axes[0].set_title("Class distribution")
axes[1].set_title("Headline word length")
plt.tight_layout()
plt.show()
'''
    ),
    md(
        """
## Формат инструкционного промпта

Модель не получает отдельную классификационную голову. Вместо этого она учится продолжать текст промпта одним символом `A` или `B`.
"""
    ),
    code(
        r'''
PROMPT_PREFIX = """### Instruction:
Decide whether the following news headline is clickbait.

Return only one label:
A = not_clickbait
B = clickbait

### Headline:
"""
PROMPT_SUFFIX = """

### Answer:
"""


def build_prompt(headline: str) -> str:
    return f"{PROMPT_PREFIX}{normalize_headline(headline)}{PROMPT_SUFFIX}"


def build_training_text(headline: str, answer: str, eos_token: str) -> str:
    return build_prompt(headline) + answer + eos_token


for _, row in train_df.sample(min(2, len(train_df)), random_state=SEED).iterrows():
    display(Markdown("```text\n" + build_prompt(row["headline"]) + row["answer"] + "\n```"))
'''
    ),
    md(
        """
## Вспомогательные функции для модели и генерации

Здесь задаются 4-битная загрузка, строгий парсер ответов `A/B` и расчет метрик. Некорректные ответы считаются ошибками и дополнительно учитываются в `invalid_count`.
"""
    ),
    code(
        r'''
def make_bnb_config() -> BitsAndBytesConfig:
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )


def load_tokenizer(model_name: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return tokenizer


def load_quantized_causal_lm(model_name: str) -> AutoModelForCausalLM:
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=make_bnb_config(),
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )
    model.config.use_cache = False
    if getattr(model.config, "pad_token_id", None) is None:
        model.config.pad_token_id = model.config.eos_token_id
    if hasattr(model, "generation_config"):
        model.generation_config.pad_token_id = model.config.pad_token_id
    return model


def load_tokenizer_and_model_with_fallback(candidates: list[str]) -> tuple[str, AutoTokenizer, AutoModelForCausalLM]:
    errors: dict[str, str] = {}
    for candidate in candidates:
        try:
            print(f"Loading model: {candidate}")
            tokenizer = load_tokenizer(candidate)
            model = load_quantized_causal_lm(candidate)
            return candidate, tokenizer, model
        except Exception as exc:
            errors[candidate] = repr(exc)
            print(f"Failed to load {candidate}: {exc}")
            clear_cuda_cache()
    raise RuntimeError(f"All model candidates failed: {errors}")


def parse_ab_answer(text: str) -> int:
    cleaned = str(text).strip().upper()
    if not cleaned:
        return -1
    # Strict mode: accept the first standalone A/B token or the first non-space char.
    first = re.match(r"^[\s`'\".:\-]*([AB])\b", cleaned)
    if first:
        return 0 if first.group(1) == "A" else 1
    token = re.search(r"\b([AB])\b", cleaned)
    if token:
        return 0 if token.group(1) == "A" else 1
    return -1


@torch.inference_mode()
def generate_ab_predictions(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    headlines: list[str],
    batch_size: int = 8,
    max_new_tokens: int = 4,
) -> tuple[np.ndarray, list[str]]:
    model.eval()
    old_padding_side = tokenizer.padding_side
    tokenizer.padding_side = "left"

    preds: list[int] = []
    raw_outputs: list[str] = []
    device = next(model.parameters()).device

    for start in range(0, len(headlines), batch_size):
        batch_headlines = headlines[start : start + batch_size]
        prompts = [build_prompt(text) for text in batch_headlines]
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
        )
        inputs = {key: value.to(device) for key, value in inputs.items()}

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
        generated_ids = outputs[:, inputs["input_ids"].shape[1] :]
        decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        raw_outputs.extend(decoded)
        preds.extend(parse_ab_answer(item) for item in decoded)

    tokenizer.padding_side = old_padding_side
    return np.array(preds, dtype=int), raw_outputs


def metrics_from_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    invalid_mask = y_pred < 0
    y_pred_for_metrics = y_pred.copy()
    # Invalid predictions are counted as wrong labels.
    y_pred_for_metrics[invalid_mask] = 1 - y_true[invalid_mask]

    report_dict = classification_report(
        y_true,
        y_pred_for_metrics,
        target_names=["not_clickbait", "clickbait"],
        output_dict=True,
        zero_division=0,
    )
    report_text = classification_report(
        y_true,
        y_pred_for_metrics,
        target_names=["not_clickbait", "clickbait"],
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred_for_metrics)),
        "precision": float(precision_score(y_true, y_pred_for_metrics, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred_for_metrics, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred_for_metrics, zero_division=0)),
        "classification_report": report_dict,
        "classification_report_text": report_text,
        "confusion_matrix": confusion_matrix(y_true, y_pred_for_metrics).tolist(),
        "invalid_count": int(invalid_mask.sum()),
        "prediction_rate": float((~invalid_mask).mean()),
    }
'''
    ),
    md(
        """
## Zero-shot оценка базовой LLM

Перед дообучением оцениваем базовую модель без LoRA на небольшой части test split. Это экономит время и дает нижнюю точку сравнения.

Размер подвыборки управляется параметром `ZERO_SHOT_N`.
"""
    ),
    code(
        r'''
zero_shot_metrics: dict[str, Any] = {
    "accuracy": float("nan"),
    "precision": float("nan"),
    "recall": float("nan"),
    "f1": float("nan"),
    "invalid_count": None,
    "prediction_rate": float("nan"),
}
zero_shot_predictions_df = pd.DataFrame()
ACTIVE_MODEL_NAME = MODEL_NAME

if ZERO_SHOT_N is not None and ZERO_SHOT_N > 0:
    zero_eval_df = stratified_sample(test_df, min(ZERO_SHOT_N, len(test_df)), SEED)
    zs_model_name, zs_tokenizer, zs_model = load_tokenizer_and_model_with_fallback(MODEL_CANDIDATES)
    ACTIVE_MODEL_NAME = zs_model_name

    start_time = time.time()
    zs_preds, zs_raw = generate_ab_predictions(
        zs_model,
        zs_tokenizer,
        zero_eval_df["headline"].tolist(),
        batch_size=GENERATION_BATCH_SIZE,
        max_new_tokens=MAX_NEW_TOKENS,
    )
    zero_shot_duration = time.time() - start_time
    zero_shot_metrics = metrics_from_predictions(zero_eval_df["label"].to_numpy(), zs_preds)
    zero_shot_metrics["duration_seconds"] = zero_shot_duration
    zero_shot_metrics["n_eval"] = int(len(zero_eval_df))
    zero_shot_metrics["model_name"] = zs_model_name

    zero_shot_predictions_df = zero_eval_df.copy()
    zero_shot_predictions_df["prediction"] = zs_preds
    zero_shot_predictions_df["raw_generation"] = zs_raw
    zero_shot_predictions_df["prediction_name"] = zero_shot_predictions_df["prediction"].map(
        {0: "not_clickbait", 1: "clickbait", -1: "INVALID"}
    )

    print("Zero-shot metrics:")
    display(pd.DataFrame([zero_shot_metrics]).drop(columns=["classification_report", "classification_report_text", "confusion_matrix"], errors="ignore"))
    print(zero_shot_metrics["classification_report_text"])

    del zs_model
    del zs_tokenizer
    clear_cuda_cache()
else:
    print("ZERO_SHOT_N <= 0, zero-shot evaluation skipped.")
'''
    ),
    md(
        """
## Загрузка QLoRA-модели

Основная модель загружается в 4-битном режиме `nf4`. Затем включается подготовка для k-bit training и добавляются LoRA-адаптеры только на проекции внимания и MLP-слои Qwen.

Полные веса LLM не дообучаются.
"""
    ),
    code(
        r'''
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
)


def attach_lora_adapters(base_model: AutoModelForCausalLM) -> AutoModelForCausalLM:
    base_model = prepare_model_for_kbit_training(base_model)
    if hasattr(base_model, "enable_input_require_grads"):
        base_model.enable_input_require_grads()
    peft_model = get_peft_model(base_model, lora_config)
    peft_model.config.use_cache = False
    return peft_model


def load_fresh_lora_model(model_name: str) -> AutoModelForCausalLM:
    base_model = load_quantized_causal_lm(model_name)
    return attach_lora_adapters(base_model)


ACTIVE_MODEL_NAME, tokenizer, base_model = load_tokenizer_and_model_with_fallback([ACTIVE_MODEL_NAME] + [m for m in MODEL_CANDIDATES if m != ACTIVE_MODEL_NAME])
model = attach_lora_adapters(base_model)


def get_trainable_parameter_stats(model: torch.nn.Module) -> dict[str, float]:
    trainable = 0
    total = 0
    for _, param in model.named_parameters():
        total += param.numel()
        if param.requires_grad:
            trainable += param.numel()
    pct = 100 * trainable / total if total else 0
    return {
        "trainable_params": int(trainable),
        "total_params": int(total),
        "trainable_percent": float(pct),
    }


trainable_stats = get_trainable_parameter_stats(model)
model.print_trainable_parameters()
print(trainable_stats)
'''
    ),
    md(
        """
## Токенизация для SFT-style causal language modeling

В `input_ids` попадает последовательность `prompt + answer + eos_token`.

В `labels` токены промпта заменяются на `-100`, поэтому loss считается только по токенам ответа `A/B` и EOS. Заголовок усекается так, чтобы метка ответа всегда оставалась в последовательности.
"""
    ),
    code(
        r'''
def tokenize_sft_example(example: dict[str, Any]) -> dict[str, list[int]]:
    answer = str(example["answer"]).strip()
    headline = normalize_headline(example["headline"])
    eos = tokenizer.eos_token or ""

    prefix_ids = tokenizer(PROMPT_PREFIX, add_special_tokens=False)["input_ids"]
    headline_ids = tokenizer(headline, add_special_tokens=False)["input_ids"]
    suffix_ids = tokenizer(PROMPT_SUFFIX, add_special_tokens=False)["input_ids"]
    target_ids = tokenizer(answer + eos, add_special_tokens=False)["input_ids"]

    fixed_len = len(prefix_ids) + len(suffix_ids) + len(target_ids)
    available_for_headline = MAX_LENGTH - fixed_len
    if available_for_headline < 1:
        raise ValueError(
            f"MAX_LENGTH={MAX_LENGTH} is too small for the prompt and answer. "
            f"Need at least {fixed_len + 1} tokens."
        )

    headline_ids = headline_ids[:available_for_headline]
    prompt_ids = prefix_ids + headline_ids + suffix_ids
    input_ids = prompt_ids + target_ids
    labels = [-100] * len(prompt_ids) + target_ids

    return {
        "input_ids": input_ids,
        "attention_mask": [1] * len(input_ids),
        "labels": labels,
    }


tokenized_dataset = DatasetDict()
for split_name, split_ds in dataset.items():
    tokenized_dataset[split_name] = split_ds.map(
        tokenize_sft_example,
        remove_columns=split_ds.column_names,
        desc=f"Tokenizing {split_name}",
    )

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True,
    label_pad_token_id=-100,
    pad_to_multiple_of=8,
)


def single_token_id(tokenizer: AutoTokenizer, text: str) -> int:
    token_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    if len(token_ids) != 1:
        raise ValueError(f"Expected {text!r} to map to one token, got token ids: {token_ids}")
    return int(token_ids[0])


A_TOKEN_ID = single_token_id(tokenizer, "A")
B_TOKEN_ID = single_token_id(tokenizer, "B")
ANSWER_TOKEN_IDS = torch.tensor([A_TOKEN_ID, B_TOKEN_ID], dtype=torch.long)
print("Answer token ids:", {"A": A_TOKEN_ID, "B": B_TOKEN_ID})


def preprocess_logits_for_metrics(logits: torch.Tensor | tuple[torch.Tensor, ...], labels: torch.Tensor) -> torch.Tensor:
    if isinstance(logits, tuple):
        logits = logits[0]
    labels = labels.to(logits.device)
    answer_mask = labels.ne(-100)
    first_answer_pos = answer_mask.int().argmax(dim=1)
    pred_pos = torch.clamp(first_answer_pos - 1, min=0)
    batch_idx = torch.arange(logits.shape[0], device=logits.device)

    answer_token_ids = ANSWER_TOKEN_IDS.to(logits.device)
    ab_logits = logits[batch_idx, pred_pos][:, answer_token_ids]

    true_token_ids = labels[batch_idx, first_answer_pos]
    true_ab = torch.full_like(first_answer_pos, fill_value=-100)
    true_ab = torch.where(true_token_ids.eq(A_TOKEN_ID), torch.zeros_like(true_ab), true_ab)
    true_ab = torch.where(true_token_ids.eq(B_TOKEN_ID), torch.ones_like(true_ab), true_ab)
    return torch.cat([ab_logits, true_ab.unsqueeze(1).to(ab_logits.dtype)], dim=1)


def compute_ab_metrics(eval_pred) -> dict[str, float]:
    packed = eval_pred.predictions
    if isinstance(packed, tuple):
        packed = packed[0]
    packed = np.asarray(packed)
    if packed.ndim == 3:
        packed = packed.reshape(-1, packed.shape[-1])

    y_true = packed[:, 2].astype(int)
    y_pred = packed[:, :2].argmax(axis=1).astype(int)
    valid_mask = y_true >= 0
    if not valid_mask.any():
        return {
            "ab_accuracy": 0.0,
            "ab_precision": 0.0,
            "ab_recall": 0.0,
            "ab_f1": 0.0,
            "ab_invalid_labels": float(len(y_true)),
        }

    y_true_valid = y_true[valid_mask]
    y_pred_valid = y_pred[valid_mask]
    return {
        "ab_accuracy": float(accuracy_score(y_true_valid, y_pred_valid)),
        "ab_precision": float(precision_score(y_true_valid, y_pred_valid, zero_division=0)),
        "ab_recall": float(recall_score(y_true_valid, y_pred_valid, zero_division=0)),
        "ab_f1": float(f1_score(y_true_valid, y_pred_valid, zero_division=0)),
        "ab_invalid_labels": float((~valid_mask).sum()),
    }

sample_item = tokenized_dataset["train"][0]
print({key: len(value) for key, value in sample_item.items()})
print("Decoded input:")
print(tokenizer.decode(sample_item["input_ids"]))
print("Decoded labels only:")
label_ids = [token_id for token_id in sample_item["labels"] if token_id != -100]
print(tokenizer.decode(label_ids))
'''
    ),
    md(
        """
## Обучение LoRA-адаптеров

Используется `Trainer` из Transformers. Сохраняется лучшая модель по validation F1 (`eval_ab_f1`), рассчитанной по прямым логитам токенов `A/B`; логирование выполняется без `wandb`.

Параметры по умолчанию рассчитаны на Kaggle GPU T4: batch size 4 на устройство и gradient accumulation 8.
"""
    ),
    code(
        r'''
training_output_dir = OUTPUT_DIR / "qwen_clickbait_lora_trainer"

training_args_signature = inspect.signature(TrainingArguments.__init__)
trainer_signature = inspect.signature(Trainer.__init__)


def build_training_arguments(
    output_dir: Path,
    do_eval: bool,
    load_best_model_at_end: bool,
) -> TrainingArguments:
    kwargs = {
        "output_dir": str(output_dir),
        "num_train_epochs": NUM_TRAIN_EPOCHS,
        "learning_rate": LEARNING_RATE,
        "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
        "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
        "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
        "fp16": bool(torch.cuda.is_available()),
        "gradient_checkpointing": True,
        "save_strategy": "epoch",
        "load_best_model_at_end": load_best_model_at_end,
        "logging_steps": LOGGING_STEPS,
        "save_total_limit": SAVE_TOTAL_LIMIT,
        "report_to": "none",
        "optim": "paged_adamw_8bit",
        "warmup_ratio": 0.03,
        "lr_scheduler_type": "cosine",
        "remove_unused_columns": False,
    }
    if do_eval:
        kwargs["metric_for_best_model"] = BEST_MODEL_METRIC
        kwargs["greater_is_better"] = True
    if "eval_strategy" in training_args_signature.parameters:
        kwargs["eval_strategy"] = "epoch" if do_eval else "no"
    else:
        kwargs["evaluation_strategy"] = "epoch" if do_eval else "no"
    return TrainingArguments(**kwargs)


def build_trainer(
    peft_model: AutoModelForCausalLM,
    args: TrainingArguments,
    train_dataset: Dataset,
    eval_dataset: Dataset | None = None,
    with_metrics: bool = True,
) -> Trainer:
    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=peft_model,
        padding=True,
        label_pad_token_id=-100,
        pad_to_multiple_of=8,
    )
    kwargs = {
        "model": peft_model,
        "args": args,
        "train_dataset": train_dataset,
        "data_collator": collator,
    }
    if eval_dataset is not None:
        kwargs["eval_dataset"] = eval_dataset
    if with_metrics:
        kwargs["compute_metrics"] = compute_ab_metrics
        kwargs["preprocess_logits_for_metrics"] = preprocess_logits_for_metrics
    if "processing_class" in trainer_signature.parameters:
        kwargs["processing_class"] = tokenizer
    else:
        kwargs["tokenizer"] = tokenizer
    return Trainer(**kwargs)


training_args = build_training_arguments(
    output_dir=training_output_dir,
    do_eval=True,
    load_best_model_at_end=True,
)
trainer = build_trainer(
    peft_model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    with_metrics=True,
)

clear_cuda_cache()
selection_start_time = time.time()
train_result = trainer.train()
selection_train_duration_seconds = time.time() - selection_start_time
val_metrics = trainer.evaluate(tokenized_dataset["validation"])
selection_history_df = pd.DataFrame(trainer.state.log_history)

print("Selection-stage train result:", train_result)
print("Validation metrics:", val_metrics)
print("Selection-stage train duration, seconds:", round(selection_train_duration_seconds, 2))

selected_adapter_dir = OUTPUT_DIR / "qwen_clickbait_lora_selected_on_val"
trainer.model.save_pretrained(selected_adapter_dir)
tokenizer.save_pretrained(selected_adapter_dir)
print("Validation-selected adapter saved to:", selected_adapter_dir)

final_train_duration_seconds = 0.0
final_train_result = None
final_history_df = pd.DataFrame()
final_training_stage = "validation_selected"

if FINAL_TRAIN_ON_TRAIN_VAL:
    print("FINAL_TRAIN_ON_TRAIN_VAL=True: fitting a fresh LoRA adapter on train+val.")
    del trainer
    del model
    clear_cuda_cache()

    model = load_fresh_lora_model(ACTIVE_MODEL_NAME)
    trainable_stats = get_trainable_parameter_stats(model)
    final_training_output_dir = OUTPUT_DIR / "qwen_clickbait_lora_train_val_trainer"
    final_training_args = build_training_arguments(
        output_dir=final_training_output_dir,
        do_eval=False,
        load_best_model_at_end=False,
    )
    trainer = build_trainer(
        peft_model=model,
        args=final_training_args,
        train_dataset=tokenized_dataset["train_val"],
        eval_dataset=None,
        with_metrics=False,
    )
    clear_cuda_cache()
    final_start_time = time.time()
    final_train_result = trainer.train()
    final_train_duration_seconds = time.time() - final_start_time
    final_history_df = pd.DataFrame(trainer.state.log_history)
    final_training_stage = "train_val_refit"
    print("Final train+val result:", final_train_result)
    print("Final train+val duration, seconds:", round(final_train_duration_seconds, 2))

train_duration_seconds = selection_train_duration_seconds + final_train_duration_seconds
if not selection_history_df.empty:
    selection_history_df["stage"] = "selection_train"
if not final_history_df.empty:
    final_history_df["stage"] = "final_train_val"
history_df = pd.concat([selection_history_df, final_history_df], ignore_index=True)
display(history_df.tail())
'''
    ),
    md(
        """
## Оценка QLoRA на train+val и test split

После обучения модель снова отвечает генерацией `A/B`. Парсер остается строгим: если модель выдала невалидный ответ, он считается ошибкой и попадает в `invalid_count`.
"""
    ),
    code(
        r'''
def evaluate_generation_dataframe(
    frame: pd.DataFrame,
    split_name: str,
    sample_n: int | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    eval_frame = stratified_sample(frame, sample_n, SEED) if sample_n is not None else frame.reset_index(drop=True).copy()
    start_time = time.time()
    preds, raw_outputs = generate_ab_predictions(
        model,
        tokenizer,
        eval_frame["headline"].tolist(),
        batch_size=GENERATION_BATCH_SIZE,
        max_new_tokens=MAX_NEW_TOKENS,
    )
    duration_seconds = time.time() - start_time
    metrics = metrics_from_predictions(eval_frame["label"].to_numpy(), preds)
    metrics["duration_seconds"] = duration_seconds
    metrics["n_eval"] = int(len(eval_frame))
    metrics["model_name"] = ACTIVE_MODEL_NAME
    metrics["training_stage"] = final_training_stage
    metrics["split"] = split_name

    pred_frame = eval_frame.copy()
    pred_frame["prediction"] = preds
    pred_frame["raw_generation"] = raw_outputs
    pred_frame["prediction_name"] = pred_frame["prediction"].map(
        {0: "not_clickbait", 1: "clickbait", -1: "INVALID"}
    )
    pred_frame["is_valid_prediction"] = pred_frame["prediction"].ge(0)
    pred_frame["is_correct"] = pred_frame["label"].eq(pred_frame["prediction"])
    pred_frame["eval_split"] = split_name
    pred_frame["word_len"] = pred_frame["headline"].str.split().str.len()
    return metrics, pred_frame


clear_cuda_cache()
train_val_eval_n = None if TRAIN_VAL_EVAL_N is None else min(TRAIN_VAL_EVAL_N, len(train_val_df))
train_val_metrics, train_val_predictions_df = evaluate_generation_dataframe(
    train_val_df,
    split_name="train+val",
    sample_n=train_val_eval_n,
)
qlora_metrics, predictions_df = evaluate_generation_dataframe(
    test_df,
    split_name="test",
    sample_n=None,
)
eval_duration_seconds = train_val_metrics["duration_seconds"] + qlora_metrics["duration_seconds"]

split_metrics_df = pd.DataFrame(
    [
        {
            "split": "train+val",
            "n_eval": train_val_metrics["n_eval"],
            "accuracy": train_val_metrics["accuracy"],
            "precision": train_val_metrics["precision"],
            "recall": train_val_metrics["recall"],
            "f1": train_val_metrics["f1"],
            "invalid_count": train_val_metrics["invalid_count"],
            "prediction_rate": train_val_metrics["prediction_rate"],
        },
        {
            "split": "test",
            "n_eval": qlora_metrics["n_eval"],
            "accuracy": qlora_metrics["accuracy"],
            "precision": qlora_metrics["precision"],
            "recall": qlora_metrics["recall"],
            "f1": qlora_metrics["f1"],
            "invalid_count": qlora_metrics["invalid_count"],
            "prediction_rate": qlora_metrics["prediction_rate"],
        },
    ]
)
display(split_metrics_df)
print("Train+val classification report:")
print(train_val_metrics["classification_report_text"])
print("Test classification report:")
print(qlora_metrics["classification_report_text"])

cm_train_val = np.array(train_val_metrics["confusion_matrix"])
cm = np.array(qlora_metrics["confusion_matrix"])
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, matrix, title in zip(axes, [cm_train_val, cm], ["train+val", "test"]):
    if sns is not None:
        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["not_clickbait", "clickbait"],
            yticklabels=["not_clickbait", "clickbait"],
            ax=ax,
        )
    else:
        ax.imshow(matrix, cmap="Blues")
        for (i, j), value in np.ndenumerate(matrix):
            ax.text(j, i, str(value), ha="center", va="center")
        ax.set_xticks([0, 1], ["not_clickbait", "clickbait"])
        ax.set_yticks([0, 1], ["not_clickbait", "clickbait"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"QLoRA confusion matrix: {title}")
plt.tight_layout()
plt.show()
'''
    ),
    md(
        """
## Анализ ошибок

Сохраняем таблицы false positive и false negative, чтобы быстро посмотреть, какие заголовки модель путает.
"""
    ),
    code(
        r'''
predictions_df = predictions_df.copy()
train_val_predictions_df = train_val_predictions_df.copy()
all_eval_predictions_df = pd.concat([train_val_predictions_df, predictions_df], ignore_index=True)

false_positives_df = predictions_df[
    predictions_df["label"].eq(0) & predictions_df["prediction"].eq(1)
].copy()
false_negatives_df = predictions_df[
    predictions_df["label"].eq(1) & predictions_df["prediction"].eq(0)
].copy()
invalid_predictions_df = predictions_df[predictions_df["prediction"].lt(0)].copy()

print("False positives:", len(false_positives_df))
display(false_positives_df[["headline", "label_name", "prediction_name", "raw_generation"]].head(20))

print("False negatives:", len(false_negatives_df))
display(false_negatives_df[["headline", "label_name", "prediction_name", "raw_generation"]].head(20))

print("Invalid predictions:", len(invalid_predictions_df))
display(invalid_predictions_df[["headline", "label_name", "raw_generation"]].head(20))
'''
    ),
    md(
        """
## Сравнение с RNN/GRU-бенчмарком teammate

В таблицу сравнения включены заданные метрики RNN/GRU, zero-shot LLM и LLM после QLoRA. Для RNN/GRU используются известные значения: test accuracy `96.12%`, test F1 `96.10%`.
"""
    ),
    code(
        r'''
comparison_df = pd.DataFrame(
    [
        {
            "method": "RNN/GRU benchmark",
            "test_accuracy": RNN_BENCHMARK["test_accuracy"],
            "test_f1": RNN_BENCHMARK["test_f1"],
            "notes": "Teammate benchmark, split 28800/1600/1600",
        },
        {
            "method": "LLM zero-shot",
            "test_accuracy": zero_shot_metrics.get("accuracy", float("nan")),
            "test_f1": zero_shot_metrics.get("f1", float("nan")),
            "notes": f"Measured on {zero_shot_metrics.get('n_eval', 0)} examples",
        },
        {
            "method": "LLM + QLoRA",
            "test_accuracy": qlora_metrics["accuracy"],
            "test_f1": qlora_metrics["f1"],
            "notes": f"Measured on full test split: {qlora_metrics['n_eval']} examples",
        },
    ]
)
display(comparison_df)

plot_df = comparison_df.melt(
    id_vars=["method"],
    value_vars=["test_accuracy", "test_f1"],
    var_name="metric",
    value_name="value",
)
fig, ax = plt.subplots(figsize=(10, 5))
if sns is not None:
    sns.barplot(data=plot_df, x="method", y="value", hue="metric", ax=ax)
else:
    pivot = plot_df.pivot(index="method", columns="metric", values="value")
    pivot.plot(kind="bar", ax=ax)
ax.set_ylim(0, 1)
ax.set_ylabel("Score")
ax.set_title("Benchmark comparison")
ax.tick_params(axis="x", rotation=15)
for container in ax.containers:
    ax.bar_label(container, fmt="%.3f", padding=3)
plt.tight_layout()
plt.show()

display(Markdown(
    "QLoRA adapts the LLM to the clickbait classification task while training only a small fraction of parameters."
))
'''
    ),
    md(
        """
## Сохранение артефактов

Сохраняются LoRA-адаптер, tokenizer, метрики, предсказания, таблицы ошибок, comparison CSV, confusion matrix и training curves.
"""
    ),
    code(
        r'''
plots_dir = OUTPUT_DIR / "plots"
plots_dir.mkdir(parents=True, exist_ok=True)
graph_artifacts: dict[str, str] = {}


def set_dark_plot_style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update(
        {
            "figure.facecolor": "#0f1218",
            "axes.facecolor": "#171b24",
            "axes.edgecolor": "#303847",
            "axes.labelcolor": "#eef2f8",
            "xtick.color": "#cbd5e1",
            "ytick.color": "#cbd5e1",
            "text.color": "#eef2f8",
            "grid.color": "#303847",
            "legend.facecolor": "#171b24",
            "legend.edgecolor": "#303847",
        }
    )


def save_current_plot(name: str) -> Path:
    path = plots_dir / name
    plt.savefig(path, dpi=180, bbox_inches="tight", facecolor=plt.gcf().get_facecolor())
    graph_artifacts[name] = str(path)
    return path


set_dark_plot_style()

metric_plot_df = split_metrics_df.melt(
    id_vars=["split"],
    value_vars=["accuracy", "precision", "recall", "f1", "prediction_rate"],
    var_name="metric",
    value_name="value",
)
fig, ax = plt.subplots(figsize=(11, 5))
if sns is not None:
    sns.barplot(data=metric_plot_df, x="metric", y="value", hue="split", palette=["#62d2a2", "#7aa7ff"], ax=ax)
else:
    metric_plot_df.pivot(index="metric", columns="split", values="value").plot(kind="bar", ax=ax)
ax.set_ylim(0, 1.02)
ax.set_title("Final QLoRA metrics: train+val vs test")
ax.set_ylabel("Score")
ax.grid(axis="y", alpha=0.25)
for container in ax.containers:
    ax.bar_label(container, fmt="%.3f", padding=3, fontsize=9)
plt.tight_layout()
save_current_plot("metrics_train_val_vs_test.png")
plt.show()

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for row_idx, (split_name, matrix) in enumerate([("train+val", cm_train_val), ("test", cm)]):
    normalized = matrix / np.maximum(matrix.sum(axis=1, keepdims=True), 1)
    for col_idx, (data, title, fmt) in enumerate(
        [
            (matrix, f"{split_name} counts", "d"),
            (normalized, f"{split_name} normalized", ".2f"),
        ]
    ):
        ax = axes[row_idx, col_idx]
        if sns is not None:
            sns.heatmap(
                data,
                annot=True,
                fmt=fmt,
                cmap="mako",
                cbar=False,
                xticklabels=["not_clickbait", "clickbait"],
                yticklabels=["not_clickbait", "clickbait"],
                ax=ax,
            )
        else:
            ax.imshow(data, cmap="viridis")
            for (i, j), value in np.ndenumerate(data):
                ax.text(j, i, format(value, fmt), ha="center", va="center")
            ax.set_xticks([0, 1], ["not_clickbait", "clickbait"])
            ax.set_yticks([0, 1], ["not_clickbait", "clickbait"])
        ax.set_title(title)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
plt.tight_layout()
save_current_plot("confusion_matrices_train_val_test.png")
plt.show()

benchmark_plot_df = comparison_df.melt(
    id_vars=["method"],
    value_vars=["test_accuracy", "test_f1"],
    var_name="metric",
    value_name="value",
)
fig, ax = plt.subplots(figsize=(11, 5))
if sns is not None:
    sns.barplot(data=benchmark_plot_df, x="method", y="value", hue="metric", palette=["#62d2a2", "#ffcf5a"], ax=ax)
else:
    benchmark_plot_df.pivot(index="method", columns="metric", values="value").plot(kind="bar", ax=ax)
ax.set_ylim(0, 1.02)
ax.set_title("RNN/GRU benchmark vs LLM baselines")
ax.set_ylabel("Score")
ax.tick_params(axis="x", rotation=12)
ax.grid(axis="y", alpha=0.25)
for container in ax.containers:
    ax.bar_label(container, fmt="%.3f", padding=3, fontsize=9)
plt.tight_layout()
save_current_plot("benchmark_comparison.png")
plt.show()

length_df = all_eval_predictions_df.copy()
length_df["length_bin"] = pd.cut(
    length_df["word_len"],
    bins=[0, 5, 10, 15, 20, 30, 1000],
    labels=["1-5", "6-10", "11-15", "16-20", "21-30", "31+"],
    include_lowest=True,
)
length_acc_df = (
    length_df.groupby(["eval_split", "length_bin"], observed=False)
    .agg(accuracy=("is_correct", "mean"), n=("headline", "size"))
    .reset_index()
)
fig, ax = plt.subplots(figsize=(11, 5))
if sns is not None:
    sns.lineplot(data=length_acc_df, x="length_bin", y="accuracy", hue="eval_split", marker="o", ax=ax)
else:
    for split_name, part in length_acc_df.groupby("eval_split"):
        ax.plot(part["length_bin"].astype(str), part["accuracy"], marker="o", label=split_name)
ax.set_ylim(0, 1.02)
ax.set_title("Accuracy by headline length")
ax.set_xlabel("Headline length, words")
ax.set_ylabel("Accuracy")
ax.grid(alpha=0.25)
ax.legend()
plt.tight_layout()
save_current_plot("accuracy_by_headline_length.png")
plt.show()

error_rows = []
for split_name, part in all_eval_predictions_df.groupby("eval_split"):
    error_rows.extend(
        [
            {"split": split_name, "type": "false_positive", "count": int(((part["label"] == 0) & (part["prediction"] == 1)).sum())},
            {"split": split_name, "type": "false_negative", "count": int(((part["label"] == 1) & (part["prediction"] == 0)).sum())},
            {"split": split_name, "type": "invalid", "count": int((part["prediction"] < 0).sum())},
        ]
    )
error_breakdown_df = pd.DataFrame(error_rows)
fig, ax = plt.subplots(figsize=(9, 5))
if sns is not None:
    sns.barplot(data=error_breakdown_df, x="type", y="count", hue="split", palette=["#62d2a2", "#ff6b7a"], ax=ax)
else:
    error_breakdown_df.pivot(index="type", columns="split", values="count").plot(kind="bar", ax=ax)
ax.set_title("Error breakdown")
ax.set_ylabel("Count")
ax.grid(axis="y", alpha=0.25)
for container in ax.containers:
    ax.bar_label(container, fmt="%d", padding=3, fontsize=9)
plt.tight_layout()
save_current_plot("error_breakdown.png")
plt.show()

if not history_df.empty:
    fig, ax = plt.subplots(figsize=(11, 5))
    for stage_name, part in history_df.groupby("stage", dropna=False):
        part = part.copy()
        label_prefix = str(stage_name)
        if "loss" in part.columns:
            train_loss = part.dropna(subset=["loss"])
            if not train_loss.empty:
                ax.plot(train_loss["step"], train_loss["loss"], marker="o", linewidth=1.8, label=f"{label_prefix} train loss")
        if "eval_loss" in part.columns:
            eval_loss = part.dropna(subset=["eval_loss"])
            if not eval_loss.empty:
                ax.plot(eval_loss["step"], eval_loss["eval_loss"], marker="s", linewidth=1.8, label=f"{label_prefix} eval loss")
    ax.set_title("Training curves by stage")
    ax.set_xlabel("Step")
    ax.set_ylabel("Loss")
    ax.grid(alpha=0.25)
    ax.legend()
    plt.tight_layout()
    save_current_plot("training_curves_staged.png")
    plt.show()

graph_artifacts_df = pd.DataFrame(
    [{"graph": name, "path": path} for name, path in graph_artifacts.items()]
)
display(graph_artifacts_df)

adapter_dir = OUTPUT_DIR / "qwen_clickbait_lora"
adapter_dir.mkdir(parents=True, exist_ok=True)
trainer.model.save_pretrained(adapter_dir)
tokenizer.save_pretrained(adapter_dir)

predictions_path = OUTPUT_DIR / "predictions.csv"
train_val_predictions_path = OUTPUT_DIR / "train_val_predictions.csv"
all_predictions_path = OUTPUT_DIR / "all_eval_predictions.csv"
comparison_path = OUTPUT_DIR / "comparison.csv"
split_metrics_path = OUTPUT_DIR / "split_metrics_train_val_test.csv"
false_positive_path = OUTPUT_DIR / "false_positives.csv"
false_negative_path = OUTPUT_DIR / "false_negatives.csv"
error_examples_path = OUTPUT_DIR / "error_examples.csv"
graph_artifacts_path = OUTPUT_DIR / "graph_artifacts.csv"
metrics_path = OUTPUT_DIR / "metrics.json"
confusion_matrix_path = OUTPUT_DIR / "confusion_matrix.png"
training_curves_path = OUTPUT_DIR / "training_curves.png"

predictions_df.to_csv(predictions_path, index=False)
train_val_predictions_df.to_csv(train_val_predictions_path, index=False)
all_eval_predictions_df.to_csv(all_predictions_path, index=False)
comparison_df.to_csv(comparison_path, index=False)
split_metrics_df.to_csv(split_metrics_path, index=False)
false_positives_df.to_csv(false_positive_path, index=False)
false_negatives_df.to_csv(false_negative_path, index=False)
graph_artifacts_df.to_csv(graph_artifacts_path, index=False)
pd.concat(
    [
        false_positives_df.assign(error_type="false_positive"),
        false_negatives_df.assign(error_type="false_negative"),
        invalid_predictions_df.assign(error_type="invalid_prediction"),
    ],
    ignore_index=True,
).to_csv(error_examples_path, index=False)

fig, ax = plt.subplots(figsize=(5, 4))
if sns is not None:
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["not_clickbait", "clickbait"],
        yticklabels=["not_clickbait", "clickbait"],
        ax=ax,
    )
else:
    ax.imshow(cm, cmap="Blues")
    for (i, j), value in np.ndenumerate(cm):
        ax.text(j, i, str(value), ha="center", va="center")
    ax.set_xticks([0, 1], ["not_clickbait", "clickbait"])
    ax.set_yticks([0, 1], ["not_clickbait", "clickbait"])
ax.set_xlabel("Predicted")
ax.set_ylabel("True")
ax.set_title("QLoRA confusion matrix")
plt.tight_layout()
plt.savefig(confusion_matrix_path, dpi=160, bbox_inches="tight")
plt.show()

if not history_df.empty:
    fig, ax = plt.subplots(figsize=(8, 4))
    if "loss" in history_df.columns:
        history_df.dropna(subset=["loss"]).plot(x="step", y="loss", ax=ax, label="train loss")
    if "eval_loss" in history_df.columns:
        history_df.dropna(subset=["eval_loss"]).plot(x="step", y="eval_loss", ax=ax, label="eval loss")
    ax.set_title("Training curves")
    ax.set_xlabel("Step")
    ax.set_ylabel("Loss")
    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(training_curves_path, dpi=160, bbox_inches="tight")
    plt.show()

metrics_payload = {
    "dataset": dataset_info,
    "model_name": ACTIVE_MODEL_NAME,
    "config": {
        "max_length": MAX_LENGTH,
        "num_train_epochs": NUM_TRAIN_EPOCHS,
        "learning_rate": LEARNING_RATE,
        "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
        "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
        "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_dropout": LORA_DROPOUT,
        "fast_dev_run": FAST_DEV_RUN,
        "zero_shot_n": ZERO_SHOT_N,
        "train_n": TRAIN_N,
        "final_train_on_train_val": FINAL_TRAIN_ON_TRAIN_VAL,
        "train_val_eval_n": TRAIN_VAL_EVAL_N,
        "team_split_dataset_dir": str(TEAM_SPLIT_DATASET_DIR),
        "best_model_metric": BEST_MODEL_METRIC,
        "leakage_policy": LEAKAGE_POLICY,
        "conflict_policy": CONFLICT_POLICY,
    },
    "trainable_parameters": trainable_stats,
    "rnn_benchmark": RNN_BENCHMARK,
    "zero_shot": zero_shot_metrics,
    "qlora_train_val": train_val_metrics,
    "qlora_test": qlora_metrics,
    "validation": val_metrics,
    "selection_train_duration_seconds": selection_train_duration_seconds,
    "final_train_duration_seconds": final_train_duration_seconds,
    "train_duration_seconds": train_duration_seconds,
    "eval_duration_seconds": eval_duration_seconds,
    "final_training_stage": final_training_stage,
    "artifacts": {
        "adapter_dir": str(adapter_dir),
        "validation_selected_adapter_dir": str(selected_adapter_dir),
        "metrics_json": str(metrics_path),
        "predictions_csv": str(predictions_path),
        "train_val_predictions_csv": str(train_val_predictions_path),
        "all_eval_predictions_csv": str(all_predictions_path),
        "comparison_csv": str(comparison_path),
        "split_metrics_csv": str(split_metrics_path),
        "graph_artifacts_csv": str(graph_artifacts_path),
        "confusion_matrix_png": str(confusion_matrix_path),
        "training_curves_png": str(training_curves_path),
        "error_examples_csv": str(error_examples_path),
        "plots": graph_artifacts,
    },
}


def make_json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(key): make_json_safe(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(value) for value in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        value = float(obj)
        return None if math.isnan(value) else value
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(make_json_safe(metrics_payload), f, ensure_ascii=False, indent=2)

print("Saved artifacts:")
for key, value in metrics_payload["artifacts"].items():
    print(f"{key}: {value}")
'''
    ),
    md(
        """
## HTML-отчет

Создаем автономный темный HTML-отчет с карточками метрик, описанием датасета, параметрами, сравнением с RNN/GRU, примерами ошибок и списком артефактов.
"""
    ),
    code(
        r'''
def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        if math.isnan(float(value)):
            return "n/a"
        return f"{100 * float(value):.2f}%"
    except Exception:
        return "n/a"


def fmt_num(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        value = float(value)
        if math.isnan(value):
            return "n/a"
        return f"{value:.{digits}f}"
    except Exception:
        return html.escape(str(value))


def df_to_dark_html(frame: pd.DataFrame, max_rows: int = 10) -> str:
    if frame is None or frame.empty:
        return "<p class='muted'>Нет данных для отображения.</p>"
    return frame.head(max_rows).to_html(index=False, escape=True, classes="data-table")


overview_cards = [
    ("Training stage", final_training_stage),
    ("Train+val F1", fmt_pct(train_val_metrics.get("f1"))),
    ("Test accuracy", fmt_pct(qlora_metrics.get("accuracy"))),
    ("Test F1", fmt_pct(qlora_metrics.get("f1"))),
    ("Val A/B F1", fmt_pct(val_metrics.get("eval_ab_f1"))),
    ("Val loss", fmt_num(val_metrics.get("eval_loss"))),
    ("Trainable params", f"{trainable_stats['trainable_percent']:.4f}%"),
    ("Train duration", f"{train_duration_seconds / 60:.1f} min"),
    ("Prediction rate", fmt_pct(qlora_metrics.get("prediction_rate"))),
]

params_table = pd.DataFrame(
    [
        {"parameter": "model_name", "value": ACTIVE_MODEL_NAME},
        {"parameter": "max_length", "value": MAX_LENGTH},
        {"parameter": "epochs", "value": NUM_TRAIN_EPOCHS},
        {"parameter": "learning_rate", "value": LEARNING_RATE},
        {"parameter": "batch_size", "value": PER_DEVICE_TRAIN_BATCH_SIZE},
        {"parameter": "gradient_accumulation", "value": GRADIENT_ACCUMULATION_STEPS},
        {"parameter": "LoRA r", "value": LORA_R},
        {"parameter": "LoRA alpha", "value": LORA_ALPHA},
        {"parameter": "LoRA dropout", "value": LORA_DROPOUT},
        {"parameter": "quantization", "value": "4-bit nf4"},
        {"parameter": "best_model_metric", "value": BEST_MODEL_METRIC},
        {"parameter": "team_split_dataset_dir", "value": str(TEAM_SPLIT_DATASET_DIR)},
        {"parameter": "leakage_policy", "value": LEAKAGE_POLICY},
        {"parameter": "conflict_policy", "value": CONFLICT_POLICY},
    ]
)

dataset_table = pd.DataFrame([dataset_info])
metrics_table = pd.DataFrame(
    [
        {
            "split": "train+val",
            "metric": "accuracy",
            "value": train_val_metrics["accuracy"],
        },
        {
            "split": "train+val",
            "metric": "precision",
            "value": train_val_metrics["precision"],
        },
        {
            "split": "train+val",
            "metric": "recall",
            "value": train_val_metrics["recall"],
        },
        {
            "split": "train+val",
            "metric": "f1",
            "value": train_val_metrics["f1"],
        },
        {
            "split": "test",
            "metric": "accuracy",
            "value": qlora_metrics["accuracy"],
        },
        {
            "split": "test",
            "metric": "precision",
            "value": qlora_metrics["precision"],
        },
        {
            "split": "test",
            "metric": "recall",
            "value": qlora_metrics["recall"],
        },
        {
            "split": "test",
            "metric": "f1",
            "value": qlora_metrics["f1"],
        },
        {
            "split": "test",
            "metric": "invalid_count",
            "value": qlora_metrics["invalid_count"],
        },
        {
            "split": "test",
            "metric": "prediction_rate",
            "value": qlora_metrics["prediction_rate"],
        },
    ]
)

artifact_rows = []
for key, value in metrics_payload["artifacts"].items():
    if isinstance(value, dict):
        for nested_key, nested_value in value.items():
            artifact_rows.append({"artifact": f"{key}/{nested_key}", "path": nested_value})
    else:
        artifact_rows.append({"artifact": key, "path": value})
artifact_table = pd.DataFrame(artifact_rows)

fp_examples = false_positives_df[["headline", "label_name", "prediction_name", "raw_generation"]]
fn_examples = false_negatives_df[["headline", "label_name", "prediction_name", "raw_generation"]]
correct_examples = predictions_df[predictions_df["is_correct"]][
    ["headline", "label_name", "prediction_name", "raw_generation"]
].head(5)

cards_html = "\n".join(
    f"<div class='card'><div class='card-label'>{html.escape(label)}</div><div class='card-value'>{html.escape(value)}</div></div>"
    for label, value in overview_cards
)
plot_gallery_html = "\n".join(
    "<figure class='plot-card'>"
    f"<img src='plots/{html.escape(Path(path).name)}' alt='{html.escape(name)}'>"
    f"<figcaption>{html.escape(name)}</figcaption>"
    "</figure>"
    for name, path in graph_artifacts.items()
)

report_html = f"""
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>LLM QLoRA Clickbait Report</title>
  <style>
    :root {{
      --bg: #0f1218;
      --panel: #171b24;
      --panel-2: #1f2530;
      --text: #eef2f8;
      --muted: #9ca9bb;
      --accent: #62d2a2;
      --accent-2: #7aa7ff;
      --danger: #ff6b7a;
      --border: #303847;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(1180px, calc(100% - 40px));
      margin: 0 auto;
      padding: 40px 0 56px;
    }}
    h1, h2, h3 {{
      margin: 0 0 14px;
      letter-spacing: 0;
    }}
    h1 {{
      font-size: 34px;
      line-height: 1.15;
    }}
    h2 {{
      margin-top: 34px;
      font-size: 22px;
      color: var(--accent);
    }}
    p {{
      color: var(--muted);
      margin: 0 0 14px;
    }}
    .hero {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
      margin-bottom: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 8px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      min-height: 76px;
    }}
    .card-label {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 6px;
    }}
    .card-value {{
      font-size: 23px;
      font-weight: 700;
      color: var(--text);
    }}
    section {{
      margin-top: 24px;
    }}
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      font-size: 14px;
    }}
    .data-table th, .data-table td {{
      border-bottom: 1px solid var(--border);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    .data-table th {{
      color: var(--accent-2);
      background: var(--panel-2);
      font-weight: 700;
    }}
    .data-table td {{
      color: var(--text);
    }}
    .muted {{
      color: var(--muted);
    }}
    .plot-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .plot-card {{
      margin: 0;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px;
    }}
    .plot-card img {{
      display: block;
      width: 100%;
      height: auto;
      border-radius: 6px;
    }}
    .plot-card figcaption {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
      word-break: break-word;
    }}
    .artifact-path {{
      color: var(--accent-2);
      word-break: break-all;
    }}
    @media (max-width: 900px) {{
      .grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .plot-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
<main>
  <div class="hero">
    <h1>LLM + QLoRA для классификации кликбейта</h1>
    <p>Instruction-style fine-tuning: модель генерирует A для not_clickbait и B для clickbait. Полная LLM не дообучается, обновляются только LoRA-адаптеры.</p>
    <div class="grid">{cards_html}</div>
  </div>

  <section>
    <h2>Датасет</h2>
    {df_to_dark_html(dataset_table, max_rows=5)}
  </section>

  <section>
    <h2>Параметры эксперимента</h2>
    {df_to_dark_html(params_table, max_rows=20)}
  </section>

  <section>
    <h2>Метрики QLoRA</h2>
    {df_to_dark_html(metrics_table, max_rows=20)}
  </section>

  <section>
    <h2>Сравнение с RNN/GRU</h2>
    <p>RNN/GRU benchmark: test accuracy 96.12%, test F1 96.10%, validation accuracy 97.44%, validation F1 97.42%.</p>
    {df_to_dark_html(comparison_df, max_rows=10)}
  </section>

  <section>
    <h2>Примеры корректных ответов</h2>
    {df_to_dark_html(correct_examples, max_rows=5)}
  </section>

  <section>
    <h2>False positives</h2>
    {df_to_dark_html(fp_examples, max_rows=10)}
  </section>

  <section>
    <h2>False negatives</h2>
    {df_to_dark_html(fn_examples, max_rows=10)}
  </section>

  <section>
    <h2>Графики</h2>
    <div class="plot-grid">{plot_gallery_html}</div>
  </section>

  <section>
    <h2>Артефакты</h2>
    {df_to_dark_html(artifact_table, max_rows=20)}
  </section>
</main>
</body>
</html>
"""

report_path = OUTPUT_DIR / "llm_lora_clickbait_report.html"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_html)

display(HTML(f"<p>HTML report saved to <code>{report_path}</code></p>"))
'''
    ),
    md(
        """
## Динамический итоговый вывод

Следующая ячейка формирует Markdown-вывод с фактическими метриками текущего запуска и сравнением с RNN/GRU.
"""
    ),
    code(
        r'''
summary_md = f"""
## Итог

QLoRA-модель `{ACTIVE_MODEL_NAME}` была дообучена в инструкционном формате: на вход подавался промпт с заголовком, а целевым ответом была одна метка `A` или `B`.

Финальная стадия обучения: **{final_training_stage}**. Если включен `FINAL_TRAIN_ON_TRAIN_VAL`, итоговый адаптер обучается на объединении train+val после выбора гиперпараметров по validation F1.

На train+val модель получила:

- accuracy: **{fmt_pct(train_val_metrics.get("accuracy"))}**
- F1: **{fmt_pct(train_val_metrics.get("f1"))}**
- precision: **{fmt_pct(train_val_metrics.get("precision"))}**
- recall: **{fmt_pct(train_val_metrics.get("recall"))}**
- prediction rate: **{fmt_pct(train_val_metrics.get("prediction_rate"))}**

На test split модель получила:

- accuracy: **{fmt_pct(qlora_metrics.get("accuracy"))}**
- F1: **{fmt_pct(qlora_metrics.get("f1"))}**
- precision: **{fmt_pct(qlora_metrics.get("precision"))}**
- recall: **{fmt_pct(qlora_metrics.get("recall"))}**
- prediction rate: **{fmt_pct(qlora_metrics.get("prediction_rate"))}**
- invalid predictions: **{qlora_metrics.get("invalid_count")}**

Бенчмарк teammate RNN/GRU:

- test accuracy: **96.12%**
- test F1: **96.10%**
- validation accuracy: **97.44%**
- validation F1: **97.42%**

QLoRA adapts the LLM to the clickbait classification task while training only a small fraction of parameters.

Ограничения: генеративная классификация медленнее обычной классификационной головы, результат зависит от качества парсинга `A/B`, а zero-shot оценка намеренно запускается только на подвыборке `ZERO_SHOT_N`, чтобы экономить GPU-время.

LoRA обучает только адаптеры, а не все параметры LLM: доля обучаемых параметров составила **{trainable_stats["trainable_percent"]:.4f}%**.
"""
display(Markdown(summary_md))
'''
    ),
    md(
        """
## Финальное резюме

Ноутбук реализует требуемый LLM + LoRA/QLoRA-подход без полной донастройки LLM. Модель решает задачу как генерацию одной метки `A/B`, а loss считается только по токенам ответа.

Для финального отчета включен режим `FINAL_TRAIN_ON_TRAIN_VAL=True`: сначала train/val используется для выбора checkpoint по `eval_ab_f1`, затем свежий LoRA-адаптер обучается на объединении train+val. Итоговые таблицы показывают метрики на train+val и test.

После запуска сравните строку `LLM + QLoRA` в `comparison.csv` и HTML-отчете с RNN/GRU-бенчмарком teammate: test accuracy `96.12%`, test F1 `96.10%`, validation accuracy `97.44%`, validation F1 `97.42%`.

Основные ограничения подхода: генерация медленнее прямой классификации, возможны невалидные ответы, а качество зависит от выбранной LLM, размера train split и числа эпох. LoRA обучает только адаптеры, поэтому число trainable parameters остается малой долей от полного размера модели.
"""
    ),
    md(
        """
## Галерея финальных графиков

Последняя ячейка автоматически выводит все сохраненные графики из `/kaggle/working/plots`, чтобы отчет завершался визуальным блоком.
"""
    ),
    code(
        r'''
from IPython.display import Image

if "graph_artifacts_df" in globals() and not graph_artifacts_df.empty:
    for _, row in graph_artifacts_df.iterrows():
        display(Markdown(f"### {row['graph']}"))
        display(Image(filename=row["path"]))
else:
    display(Markdown("Графики не найдены. Проверьте, что ячейка сохранения артефактов была выполнена."))
'''
    ),
]


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main() -> None:
    NOTEBOOK_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {NOTEBOOK_PATH.resolve()}")
    print(f"Cells: {len(cells)}")


if __name__ == "__main__":
    main()
