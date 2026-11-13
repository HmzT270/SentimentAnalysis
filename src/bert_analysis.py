"""
BERT ile duygu analizi.

Iki ayri model kullanilir:
  - Ingilizce: j-hartmann/sentiment-roberta-large-english-3-classes
  - Turkce:    gmzx/berturk-turkish-sentiment

Her dil icin adimlar:
  1. Veri setini oku
  2. Modeli yukle
  3. Yorumlari siniflandir
  4. Gercek etiketlerle karsilastir
  5. Sonuclari CSV olarak kaydet
"""

from pathlib import Path
import gc

import pandas as pd
import torch
from transformers import pipeline


# --- Yollar -----------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results" / "bert"


# --- Ayarlar ----------------------------------------------------------------

# Dil -> Hugging Face model adi
MODELS = {
    "Ingilizce": "j-hartmann/sentiment-roberta-large-english-3-classes",
    "Turkce": "gmzx/berturk-turkish-sentiment",
}

# Modelin dondurdugu etiket (kucuk harf) -> ortak etiket
LABEL_MAP = {
    "positive": "positive",
    "pozitif": "positive",
    "negative": "negative",
    "negatif": "negative",
    "neutral": "neutral",
    "notr": "neutral",
    "nötr": "neutral",
}

SENTIMENT_LABELS = ["positive", "negative", "neutral"]

MAX_TOKENS = 256       # Bir yorumun modele verilen en fazla token sayisi
BATCH_SIZE = 16        # Ayni anda siniflandirilan yorum sayisi
DEVICE = 0 if torch.cuda.is_available() else -1  # 0: GPU, -1: CPU


# --- Adimlar ----------------------------------------------------------------

def load_dataset(language):
    """Dile ait yorum veri setini okur. Beklenen sutunlar: text, label."""
    return pd.read_csv(DATA_DIR / f"{language}_3000.csv")


def load_classifier(language):
    """Dile uygun BERT modelini yukler."""
    return pipeline(
        "text-classification",
        model=MODELS[language],
        device=DEVICE,
    )


def to_common_label(model_label):
    """Modelin etiketini positive / negative / neutral'a cevirir."""
    key = model_label.lower().strip()
    if key not in LABEL_MAP:
        raise ValueError(f"Bilinmeyen model etiketi: {key}")
    return LABEL_MAP[key]


def predict(classifier, texts):
    """Yorumlari BATCH_SIZE'lik gruplar halinde siniflandirir.

    Dondurur: (tahmin etiketleri, guven skorlari)
    """
    labels = []
    scores = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        results = classifier(batch, truncation=True, max_length=MAX_TOKENS)

        for result in results:
            labels.append(to_common_label(result["label"]))
            scores.append(result["score"])

        print(
            f"Analiz edilen: {len(labels)}/{len(texts)}",
            end="\r",
            flush=True,
        )

    return labels, scores


def evaluate(df):
    """Genel dogrulugu ve sinif bazinda yanlis tahmin sayisini yazdirir."""
    accuracy = df["correct"].mean() * 100

    print(f"Toplam yorum: {len(df)}")
    print(f"Dogruluk: %{accuracy:.2f}")

    for label in SENTIMENT_LABELS:
        subset = df[df["label"] == label]
        errors = (~subset["correct"]).sum()
        print(f"{label} hatali tahmin: {errors}")


def save_results(df, language):
    """Sonuclari results/bert/<dil>_bert.csv olarak kaydeder."""
    output = RESULTS_DIR / f"{language.lower()}_bert.csv"
    df.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"Sonuclar kaydedildi: {output}")


def release_memory(classifier):
    """Modeli bellekten atar; ikinci dil icin GPU bellegi bosalir."""
    del classifier
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


# --- Ana akis ---------------------------------------------------------------

def analyze(language):
    """Tek bir dil icin BERT analizini bastan sona calistirir."""
    print(f"\n{language} BERT analizi basliyor...")

    df = load_dataset(language)
    classifier = load_classifier(language)

    predictions, scores = predict(classifier, df["text"].astype(str).tolist())

    df["prediction"] = predictions
    df["confidence"] = scores
    df["correct"] = df["label"] == df["prediction"]

    print(f"\n\n{language} BERT Sonuclari")
    evaluate(df)
    save_results(df, language)
    release_memory(classifier)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    device_name = (
        torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    )
    print("Kullanilan cihaz:", device_name)

    analyze("Ingilizce")
    analyze("Turkce")

    print("\nBERT analizleri tamamlandi!")


if __name__ == "__main__":
    main()
