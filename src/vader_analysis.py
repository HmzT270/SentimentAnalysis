
from pathlib import Path

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results/vader"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def predict_sentiment(text):
    score = analyzer.polarity_scores(str(text))["compound"]

    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


def analyze(filename, language, text_column="text"):
    df = pd.read_csv(DATA_DIR / filename)

    df["prediction"] = df[text_column].apply(predict_sentiment)
    df["correct"] = df["label"] == df["prediction"]

    accuracy = df["correct"].mean() * 100

    print(f"\n{language} VADER Sonuclari")
    print(f"Toplam yorum: {len(df)}")
    print(f"Dogruluk: %{accuracy:.2f}")

    for label in ["positive", "negative", "neutral"]:
        subset = df[df["label"] == label]
        errors = (~subset["correct"]).sum()
        print(f"{label} hatali tahmin: {errors}")

    output = RESULTS_DIR / f"{language.lower()}_vader.csv"

    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Sonuclar kaydedildi: {output}")


if __name__ == "__main__":
    translated_path = DATA_DIR / "Turkce_3000_translated.csv"
    if not translated_path.exists():
        raise SystemExit(
            "Yeni Turkce_3000.csv icin once text,label,text_en sutunlu "
            "Turkce_3000_translated.csv hazirlanmali. Eski arsiv cevirisini kullanmayin."
        )
    translated = pd.read_csv(translated_path)
    source = pd.read_csv(DATA_DIR / "Turkce_3000.csv")
    if (
        not {"text", "label", "text_en"}.issubset(translated.columns)
        or not translated[["text", "label"]].equals(source[["text", "label"]])
        or translated["text_en"].isna().any()
        or translated["text_en"].astype(str).str.strip().eq("").any()
    ):
        raise SystemExit("Turkce ceviri yeni veriyle eslesmiyor veya bos ceviriler var.")

    # İngilizce: Orijinal yorumlar
    analyze(
        "Ingilizce_3000.csv",
        "Ingilizce"
    )

    # Türkçe: İngilizceye çevrilmiş yorumlar
    analyze(
        "Turkce_3000_translated.csv",
        "Turkce",
        text_column="text_en"
    )
