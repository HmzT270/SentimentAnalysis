
from pathlib import Path
import gc

import pandas as pd
import torch
from transformers import pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results/bert"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    "Ingilizce": "j-hartmann/sentiment-roberta-large-english-3-classes",
    "Turkce": "gmzx/berturk-turkish-sentiment"
}

LABEL_MAP = {
    "positive": "positive",
    "pozitif": "positive",
    "negative": "negative",
    "negatif": "negative",
    "neutral": "neutral",
    "notr": "neutral",
    "nötr": "neutral"
}

DEVICE = 0 if torch.cuda.is_available() else -1
BATCH_SIZE = 16


def analyze(language):
    print(f"\n{language} BERT analizi basliyor...")

    df = pd.read_csv(
        DATA_DIR / f"{language}_3000.csv"
    )

    classifier = pipeline(
        "text-classification",
        model=MODELS[language],
        device=DEVICE
    )

    predictions = []
    scores = []

    for i in range(0, len(df), BATCH_SIZE):
        texts = df["text"].iloc[
            i:i + BATCH_SIZE
        ].astype(str).tolist()

        results = classifier(
            texts,
            batch_size=BATCH_SIZE,
            truncation=True,
            max_length=256
        )

        for result in results:
            label = result["label"].lower().strip()

            if label not in LABEL_MAP:
                raise ValueError(
                    f"Bilinmeyen model etiketi: {label}"
                )

            predictions.append(LABEL_MAP[label])
            scores.append(result["score"])

        print(
            f"Analiz edilen: {len(predictions)}/{len(df)}",
            end="\r",
            flush=True
        )

    df["prediction"] = predictions
    df["confidence"] = scores
    df["correct"] = df["label"] == df["prediction"]

    accuracy = df["correct"].mean() * 100

    print(f"\n\n{language} BERT Sonuclari")
    print(f"Toplam yorum: {len(df)}")
    print(f"Dogruluk: %{accuracy:.2f}")

    for label in ["positive", "negative", "neutral"]:
        subset = df[df["label"] == label]
        errors = (~subset["correct"]).sum()

        print(f"{label} hatali tahmin: {errors}")

    output = RESULTS_DIR / (
        f"{language.lower()}_bert.csv"
    )

    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Sonuclar kaydedildi: {output}")

    del classifier
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()


if __name__ == "__main__":
    print(
        "Kullanilan cihaz:",
        torch.cuda.get_device_name(0)
        if torch.cuda.is_available() else "CPU"
    )

    analyze("Ingilizce")
    analyze("Turkce")

    print("\nBERT analizleri tamamlandi!")
