# Usage Notes

## Kaggle QLoRA Clickbait Notebook

Feature file: `llm_lora_clickbait_kaggle.ipynb`

Purpose: fine-tune a small instruction LLM with LoRA/QLoRA for binary clickbait headline classification on the team pre-split Kaggle dataset.

How to use:

1. Upload or open `llm_lora_clickbait_kaggle.ipynb` in Kaggle.
2. Attach the team Kaggle dataset so the files are available at `/kaggle/input/datasets/kvdep1/clickbait-dataset-split`.
3. Confirm the dataset directory contains `train.csv`, `val.csv`, and `test.csv`.
4. Enable a GPU accelerator. The default settings are intended for Kaggle T4 and also work when only one GPU is effectively used.
5. Run all cells from top to bottom.
6. Review saved outputs in `/kaggle/working`.

Important configuration options:

- `MODEL_NAME`: primary model. Default is `Qwen/Qwen2.5-1.5B-Instruct`.
- `FALLBACK_MODEL_NAMES`: optional model names to try if `TRY_FALLBACK_MODELS=True`.
- `FAST_DEV_RUN`: set to `True` for a quick smoke test with 1000 train, 200 validation, and 200 test samples.
- `ZERO_SHOT_N`: number of test examples used for zero-shot baseline evaluation before LoRA training. Default is `300`.
- `TRAIN_N`: optional train subset size. Leave as `None` for the full train split.
- `MAX_LENGTH`: tokenized prompt plus answer length. Default is `160`.
- `TEAM_SPLIT_DATASET_DIR`: expected team split path. Default is `/kaggle/input/datasets/kvdep1/clickbait-dataset-split`.
- `BEST_MODEL_METRIC`: checkpoint selection metric. Default is `eval_ab_f1`, computed from direct `A/B` answer-token logits on validation.
- `FINAL_TRAIN_ON_TRAIN_VAL`: default `True`. Runs a second fresh LoRA fit on `train+val` after the validation-selected stage fixes the training recipe.
- `TRAIN_VAL_EVAL_N`: default `None`. Evaluates the final model on the full `train+val` table; set an integer for a faster partial report.
- `LEAKAGE_POLICY`: default `raise`. Stops the run if canonical headline keys overlap across train/val/test. Set to `drop_eval_duplicates` only if you explicitly want to remove overlapping validation/test rows.
- `CONFLICT_POLICY`: default `drop`. Removes canonical duplicate headlines that have conflicting labels before splitting.

Generated Kaggle artifacts:

- `/kaggle/working/qwen_clickbait_lora`: saved LoRA adapter and tokenizer.
- `/kaggle/working/metrics.json`: dataset, training, zero-shot, QLoRA, and benchmark metrics.
- `/kaggle/working/predictions.csv`: full test predictions.
- `/kaggle/working/train_val_predictions.csv`: final model predictions on train+val.
- `/kaggle/working/all_eval_predictions.csv`: combined train+val and test predictions.
- `/kaggle/working/comparison.csv`: RNN/GRU benchmark vs zero-shot LLM vs QLoRA LLM.
- `/kaggle/working/split_metrics_train_val_test.csv`: final metrics table for train+val and test.
- `/kaggle/working/false_positives.csv`: false positive examples.
- `/kaggle/working/false_negatives.csv`: false negative examples.
- `/kaggle/working/error_examples.csv`: combined error examples.
- `/kaggle/working/graph_artifacts.csv`: manifest of generated visualization files.
- `/kaggle/working/plots/`: final dark-style graphs, including metrics, benchmark, confusion matrices, length accuracy, errors, and staged training curves.
- `/kaggle/working/confusion_matrix.png`: confusion matrix plot.
- `/kaggle/working/training_curves.png`: loss curves when Trainer logs are available.
- `/kaggle/working/llm_lora_clickbait_report.html`: dark HTML report for submission review, including an embedded plot gallery.

## Regenerating the Notebook

Feature file: `tools/generate_clickbait_lora_notebook.py`

How to use:

1. From the project root, run:

   ```powershell
   python tools/generate_clickbait_lora_notebook.py
   ```

2. The script writes `llm_lora_clickbait_kaggle.ipynb` with UTF-8 encoding.
3. Open the generated notebook in Kaggle and run it with the dataset attached.
