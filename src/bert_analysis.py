"""
BERT ile duygu analizi.

Her dil icin ayri bir Hugging Face modeli kullanilir. Yorumlar siniflandirilir,
tahminler gercek etiketlerle karsilastirilir ve sonuclar CSV olarak kaydedilir.
"""

import gc
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import classification_report
from transformers import pipeline


# ---------------------------------------------------------------------------
# Yollar ve ayarlar
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results" / "bert"

MAX_TOKENS = 256  # Bir yorumun modele verilen en fazla token sayisi
BATCH_SIZE = 16   # Ayni anda siniflandirilan yorum sayisi
DEVICE = 0 if torch.cuda.is_available() else -1  # 0: GPU, -1: CPU

POSITIVE = "positive"
NEGATIVE = "negative"
NEUTRAL = "neutral"
SENTIMENT_LABELS = (POSITIVE, NEGATIVE, NEUTRAL)

EXPECTED_PER_LABEL = 1000  # Her sinif icin beklenen ornek sayisi
EXPECTED_ROWS = EXPECTED_PER_LABEL * len(SENTIMENT_LABELS)  # 3000

# Modelin dondurdugu etiketler (kucuk harf) -> ortak etiket.
# Hem Ingilizce hem Turkce etiket adlari kabul edilir.
MODEL_LABEL_TO_SENTIMENT = {
    "positive": POSITIVE,
    "pozitif": POSITIVE,
    "negative": NEGATIVE,
    "negatif": NEGATIVE,
    "neutral": NEUTRAL,
    "notr": NEUTRAL,
    "nötr": NEUTRAL,
}


@dataclass(frozen=True)
class LanguageConfig:
    """Bir dilin analizinde kullanilan dosya ve model bilgileri."""

    name: str     # Ekranda gorunen ad
    dataset: str  # data/ klasorundeki veri dosyasi
    model: str    # Hugging Face model adi
    output: str   # results/bert/ klasorundeki cikti dosyasi


LANGUAGES = [
    LanguageConfig(
        name="İngilizce",
        dataset="Ingilizce_3000.csv",
        model="j-hartmann/sentiment-roberta-large-english-3-classes",
        output="ingilizce_bert.csv",
    ),
    LanguageConfig(
        name="Türkçe",
        dataset="Turkce_3000.csv",
        model="gmzx/berturk-turkish-sentiment",
        output="turkce_bert.csv",
    ),
]


# ---------------------------------------------------------------------------
# Veri dogrulama
# ---------------------------------------------------------------------------

def validate_dataset(df: pd.DataFrame) -> None:
    """Veri setinin beklenen yapida oldugunu kontrol eder; degilse hata verir."""
    missing = {"text", "label"} - set(df.columns)
    if missing:
        raise ValueError(f"Veri setinde zorunlu sütun eksik: {sorted(missing)}")

    if df["text"].isna().any():
        raise ValueError("Boş yorum (NaN) bulundu.")
    if df["text"].astype(str).str.strip().eq("").any():
        raise ValueError("İçinde sadece boşluk olan yorum bulundu.")

    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            f"Veri seti {EXPECTED_ROWS} yorum içermeli, {len(df)} bulundu."
        )

    counts = df["label"].value_counts()
    for sentiment in SENTIMENT_LABELS:
        found = counts.get(sentiment, 0)
        if found != EXPECTED_PER_LABEL:
            raise ValueError(
                f"{sentiment}: {EXPECTED_PER_LABEL} örnek bekleniyor, {found} bulundu."
            )


# ---------------------------------------------------------------------------
# Siniflandirma
# ---------------------------------------------------------------------------

def to_sentiment(model_label: str) -> str:
    """Modelin etiketini positive / negative / neutral olarak çevirir."""
    key = model_label.lower().strip()
    if key not in MODEL_LABEL_TO_SENTIMENT:
        raise ValueError(f"Bilinmeyen model etiketi: {key}")
    return MODEL_LABEL_TO_SENTIMENT[key]


def classify(classifier, texts: list[str]) -> tuple[list[str], list[float]]:
    """Yorumları BATCH_SIZE'lık gruplar halinde sınıflandırır.

    Dondurur: (tahmin edilen etiketler, güven skorları)
    """
    sentiments: list[str] = []
    confidences: list[float] = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]

        # batch_size verilmezse pipeline varsayılan olarak 1 kullanır ve
        # yorumları tek tek işler; gerçek batching için açıkça belirtilir.
        predictions = classifier(
            batch,
            batch_size=BATCH_SIZE,
            truncation=True,
            max_length=MAX_TOKENS,
        )

        for prediction in predictions:
            sentiments.append(to_sentiment(prediction["label"]))
            confidences.append(prediction["score"])

        print(
            f"Analiz edilen: {len(sentiments)}/{len(texts)}",
            end="\r",
            flush=True,
        )

    return sentiments, confidences


def run_model(config: LanguageConfig) -> pd.DataFrame:
    """Veri setini modelle sınıflandırır ve tahminleri tabloya ekler.

    Model bu fonksiyon bitince kapsam dışına çıkar; GPU belleği
    free_gpu_memory() ile boşaltılır.
    """
    df = pd.read_csv(DATA_DIR / config.dataset)
    validate_dataset(df)

    classifier = pipeline(
        "text-classification",
        model=config.model,
        device=DEVICE,
    )

    sentiments, confidences = classify(
        classifier, df["text"].astype(str).tolist()
    )

    df["prediction"] = sentiments
    df["confidence"] = confidences
    df["correct"] = df["label"] == df["prediction"]
    return df


# ---------------------------------------------------------------------------
# Raporlama ve kayit
# ---------------------------------------------------------------------------

def print_report(df: pd.DataFrame, title: str) -> None:
    """Doğruluk, sınıf bazlı hatalar ve precision / recall / F1 değerlerini yazdırır."""
    print(f"\n\n{title}")
    print(f"Toplam yorum: {len(df)}")
    print(f"Doğruluk: %{df['correct'].mean() * 100:.2f}")

    for sentiment in SENTIMENT_LABELS:
        subset = df[df["label"] == sentiment]
        wrong = (~subset["correct"]).sum()
        print(f"{sentiment} hatalı tahmin: {wrong}")

    print("\nDetaylı performans:")
    print(
        classification_report(
            df["label"],
            df["prediction"],
            labels=list(SENTIMENT_LABELS),
            digits=4,
            zero_division=0.0,
        )
    )


def save_results(df: pd.DataFrame, output: str) -> None:
    """Sonuç tablosunu results/bert/ altına CSV olarak yazar."""
    path = RESULTS_DIR / output
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Sonuçlar kaydedildi: {path}")


def free_gpu_memory() -> None:
    """Model artık kullanılmadığında GPU önbelleğini boşaltır."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


# ---------------------------------------------------------------------------
# Ana akis
# ---------------------------------------------------------------------------

def analyze(config: LanguageConfig) -> None:
    """Tek bir dil için sınıflandırma, rapor ve kayıt adımlarını çalıştırır."""
    print(f"\n{config.name} BERT analizi başlıyor...")

    df = run_model(config)
    print_report(df, f"{config.name} BERT Sonuçları")
    save_results(df, config.output)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    device_name = (
        torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    )
    print("Kullanılan cihaz:", device_name)

    for config in LANGUAGES:
        analyze(config)
        free_gpu_memory()

    print("\nBERT analizleri tamamlandı!")


if __name__ == "__main__":
    main()
