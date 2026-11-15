
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "comparison"
OUTPUT.mkdir(parents=True, exist_ok=True)

LANGUAGES = {
    "İngilizce": "ingilizce",
    "Türkçe": "turkce"
}

# Dosya adındaki dil kodu -> grafiklerde görünen ad (Türkçe karakterli).
LANGUAGE_NAMES = {code: name for name, code in LANGUAGES.items()}

MODELS = ["VADER", "BERT", "Claude"]
LABELS = ["positive", "negative", "neutral"]


def load_results(language, model):
    name = f"{language}_{model.lower()}.csv"
    path = RESULTS / model.lower() / name

    df = pd.read_csv(path, encoding="utf-8-sig")

    # Claude'un sonuçları paralel çalıştığı için
    # orijinal yorum sırasına geri getiriliyor.
    if "row_id" in df.columns:
        if df["row_id"].duplicated().any():
            raise ValueError(f"Tekrarlanan ID: {path}")
        df = df.sort_values("row_id")

    df = df.reset_index(drop=True)

    if len(df) != 3000:
        raise ValueError(f"{path}: 3000 sonuç bulunamadı!")

    for column in ["label", "prediction"]:
        df[column] = df[column].astype(str).str.strip().str.lower()

        if not df[column].isin(LABELS).all():
            raise ValueError(f"{path}: Geçersiz {column} değeri!")

    # Sonuçların doğru veri setine ait olduğunu doğrula.
    source = pd.read_csv(
        ROOT / "data" / f"{language.capitalize()}_3000.csv"
    )

    if not df["label"].equals(
        source["label"].astype(str).str.strip().str.lower()
    ):
        raise ValueError(f"Etiket sırası uyuşmuyor: {path}")

    if "text" in df.columns and not df["text"].fillna("").astype(str).equals(
        source["text"].fillna("").astype(str)
    ):
        raise ValueError(f"Yorum sırası uyuşmuyor: {path}")

    return df


def create_confusion_matrix(matrix, language, model):
    """
    Her model ve dil için karışıklık matrisi
    görselini PNG olarak kaydeder.
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    image = ax.imshow(
        matrix.values,
        cmap="Blues",
        vmin=0,
        vmax=1000
    )

    ax.set_xticks(range(len(LABELS)), LABELS)
    ax.set_yticks(range(len(LABELS)), LABELS)

    ax.set_xlabel("Tahmin Edilen")
    ax.set_ylabel("Gerçek")
    ax.set_title(
        f"{model} - {LANGUAGE_NAMES[language]} Karışıklık Matrisi"
    )

    # Her hücreye tahmin sayısını yaz.
    for i in range(len(LABELS)):
        for j in range(len(LABELS)):
            value = matrix.iloc[i, j]

            ax.text(
                j,
                i,
                str(value),
                ha="center",
                va="center",
                color="white" if value > 500 else "black",
                fontsize=13,
                fontweight="bold"
            )

    fig.colorbar(image, ax=ax, label="Yorum Sayısı")
    fig.tight_layout()

    filename = f"{language}_{model.lower()}_confusion_matrix.png"
    output_path = OUTPUT / filename

    fig.savefig(output_path, dpi=200)
    plt.close(fig)

    print(f"Karışıklık matrisi kaydedildi: {output_path}")


def evaluate(language, model):
    df = load_results(language, model)
    correct = df["label"] == df["prediction"]

    result = {
        "Dil": language,
        "Model": model,
        "Toplam": len(df),
        "Doğru": int(correct.sum()),
        "Hatalı": int((~correct).sum()),
        "Doğruluk (%)": round(correct.mean() * 100, 2)
    }

    for label in LABELS:
        mask = df["label"] == label
        result[f"{label} hata"] = int(
            (df.loc[mask, "prediction"] != label).sum()
        )

    matrix = pd.crosstab(
        df["label"],
        df["prediction"],
        rownames=["Gerçek"],
        colnames=["Tahmin"]
    ).reindex(
        index=LABELS,
        columns=LABELS,
        fill_value=0
    )

    print(f"\n{model} - {language}")
    print(f"Doğruluk: %{result['Doğruluk (%)']:.2f}")
    print(f"Toplam hata: {result['Hatalı']}")
    print("Karışıklık matrisi:")
    print(matrix.to_string())

    # Karışıklık matrisini PNG olarak oluştur.
    create_confusion_matrix(matrix, language, model)

    return result


def create_chart(summary):
    """
    İngilizce ve Türkçe model doğruluklarını
    karşılaştıran sütun grafiğini oluşturur.
    """
    x = np.arange(len(MODELS))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, language in enumerate(LANGUAGES):
        values = [
            summary.loc[
                (summary["Dil"] == language)
                & (summary["Model"] == model),
                "Doğruluk (%)"
            ].iloc[0]
            for model in MODELS
        ]

        bars = ax.bar(
            x + (i - 0.5) * width,
            values,
            width,
            label=language
        )

        ax.bar_label(
            bars,
            fmt="%.2f%%",
            padding=3
        )

    ax.set_xticks(x, MODELS)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Doğruluk (%)")
    ax.set_title("Duygu Analizi - Model Karşılaştırması")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()

    output_path = OUTPUT / "model_karsilastirma.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)

    print(f"\nModel karşılaştırma grafiği kaydedildi: {output_path}")


def main():
    records = []

    for language, filename in LANGUAGES.items():
        for model in MODELS:
            records.append(evaluate(filename, model))
            records[-1]["Dil"] = language

    summary = pd.DataFrame(records)

    summary.to_csv(
        OUTPUT / "model_karsilastirma.csv",
        index=False,
        encoding="utf-8-sig"
    )

    create_chart(summary)

    print("\n" + "=" * 60)
    print("GENEL KARŞILAŞTIRMA")
    print("=" * 60)
    print(summary.to_string(index=False))

    print("\nSonuçlar results/comparison/ klasörüne kaydedildi.")


if __name__ == "__main__":
    main()
