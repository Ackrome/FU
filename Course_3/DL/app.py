
import streamlit as st
import torch
import torch.nn as nn
import pytorch_lightning as pl
import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path


class FocalLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2.0, reduction="mean"):
        super().__init__()
        if alpha is not None:
            self.register_buffer('alpha', torch.tensor(alpha, dtype=torch.float32))
        else:
            self.register_buffer('alpha', None)
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits, target):
        ce_loss = nn.CrossEntropyLoss(weight=self.alpha, reduction="none")(logits, target)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        return focal_loss

class SimpleNN(pl.LightningModule):
    def __init__(self, input_dim, num_classes, lr=1e-3, alpha=None):
        super().__init__()
        self.save_hyperparameters()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.BatchNorm1d(16),
            nn.Linear(16, num_classes)
        )
        self.loss_fn = FocalLoss(alpha=alpha, gamma=2.0)

    def forward(self, x):
        return self.model(x)

@st.cache_resource
def load_prediction_artifacts(artifacts_dir="artifacts"):
    artifacts_path = Path(artifacts_dir)
    with open(artifacts_path / "metadata.json", 'r') as f:
        metadata = json.load(f)
    checkpoint_path = metadata["pytorch_lightning_checkpoint"]
    model = SimpleNN.load_from_checkpoint(checkpoint_path, map_location=torch.device('cpu'))
    model.eval()
    scaler = joblib.load(metadata["scaler"])
    label_encoders = {}
    for name, path in metadata["label_encoders"].items():
        label_encoders[name] = joblib.load(path)
    print("Артефакты для предсказания успешно загружены.")
    return {
        "model": model,
        "scaler": scaler,
        "label_encoders": label_encoders,
        "metadata": metadata
    }

def predict_quality(age, coffee_intake, bmi, smoking, alcohol_consumption, occupation, artifacts):
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    label_encoders = artifacts["label_encoders"]

    num_features = np.array([[age, coffee_intake, bmi]], dtype=np.float32)
    scaled_num_features = scaler.transform(num_features)

    smoking_str = '1' if smoking else '0'
    alcohol_str = '1' if alcohol_consumption else '0'

    smoking_encoded = label_encoders["Smoking"].transform([smoking_str])[0]
    alcohol_encoded = label_encoders["Alcohol_Consumption"].transform([alcohol_str])[0]
    occupation_encoded = label_encoders["Occupation"].transform([occupation])[0]

    cat_features = np.array([[smoking_encoded, alcohol_encoded, occupation_encoded]], dtype=np.float32)

    all_features = np.concatenate([scaled_num_features, cat_features], axis=1)

    input_tensor = torch.from_numpy(all_features).to(model.device)
    with torch.no_grad():
        logits = model(input_tensor)

    probabilities = torch.softmax(logits, dim=1).cpu().numpy().flatten()

    le_target = label_encoders["Sleep_Quality"]
    class_names = le_target.classes_
    result_df = pd.DataFrame([probabilities], columns=class_names)

    return result_df

st.title('Пресказываем качество сна')

artifacts = load_prediction_artifacts()
le_occupation = artifacts["label_encoders"]["Occupation"]
le_target = artifacts["label_encoders"]["Sleep_Quality"]
num_classes = len(le_target.classes_)

st.header('Введите параметры')

age = st.slider('Возраст', 18, 100, 30)
coffee_intake = st.slider('Потребление кофе (чашек в день)', 0, 10, 2)
bmi = st.slider('Индекс массы тела', 15.0, 40.0, 22.5, 0.1)

occupation = st.selectbox('Профессия', options=le_occupation.classes_)

smoking = st.checkbox('Курите?')
alcohol_consumption = st.checkbox('Употребляете алкоголь?')

st.header('Параметры диаграммы')
top_k = st.slider('Количество топ-к классов для отображения', min_value=1, max_value=num_classes, value=3)


if st.button('Узнать качество сна'):
    probabilities_df = predict_quality(
        age, coffee_intake, bmi, smoking, alcohol_consumption, occupation, artifacts
    )

    predicted_class_name = probabilities_df.idxmax(axis=1)[0]
    confidence = probabilities_df.max(axis=1)[0]

    st.subheader("Результат предсказаний")

    col1, col2 = st.columns(2)
    col1.metric("Предсказанное качество сна", predicted_class_name)
    col2.metric("Уверенность", f"{confidence * 100:.2f}%")

    st.subheader(f'Топ {top_k} предсказаний')

    top_k_preds = probabilities_df.T.sort_values(by=0, ascending=False).head(top_k)
    top_k_preds.columns = ['Probability']
    top_k_preds.index.name = 'Качество сна'

    st.bar_chart(top_k_preds)
