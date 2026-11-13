
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "comparison"
OUTPUT.mkdir(parents=True, exist_ok=True)

LANGUAGES = {"ingilizce": "İngilizce", "turkce": "Türkçe"}
MODELS = ["vader", "bert", "claude"]
LABELS = ["positive", "negative", "neutral"]
REVIEW_COLUMNS = ["manuel_inceleme", "aciklama", "inceleme_kaynagi"]


def preserve_reviews(examples, path):
    """Keep annotations only while the text, gold label and all predictions match."""
    examples = examples.copy()
    for column in REVIEW_COLUMNS:
        examples[column] = ""
    if not path.exists():
        return examples
    saved = pd.read_csv(path, dtype=str, keep_default_na=False)
    keys = ["dil", "yorum_id"]
    identity = ["yorum", "gercek_etiket", *MODELS]
    if not set(keys + identity).issubset(saved.columns):
        raise ValueError(f"Onceki hata dosyasinin sutunlari eksik: {path}")
    if saved.duplicated(keys).any():
        raise ValueError(f"Onceki hata dosyasinda tekrar eden yorum kimligi: {path}")
    previous = saved.set_index(keys)
    for index, row in examples.iterrows():
        key = (str(row["dil"]), str(row["yorum_id"]))
        if key not in previous.index:
            continue
        old = previous.loc[key]
        if all(str(row[column]) == old[column] for column in identity):
            for column in REVIEW_COLUMNS:
                if column in saved.columns:
                    examples.at[index, column] = old[column]
    return examples


def load_language(language, display_name):
    source = pd.read_csv(
        ROOT / "data" / f"{language.capitalize()}_3000.csv"
    ).reset_index(drop=True)

    data = pd.DataFrame({
        "dil": display_name,
        "yorum_id": range(len(source)),
        "yorum": source["text"],
        "gercek_etiket": source["label"]
    })

    for model in MODELS:
        path = ROOT / "results" / model / f"{language}_{model}.csv"
        result = pd.read_csv(path)

        if "row_id" in result.columns:
            if (
                result["row_id"].duplicated().any()
                or set(result["row_id"]) != set(range(len(source)))
            ):
                raise ValueError(f"Geçersiz yorum ID: {path}")

            result = result.sort_values("row_id")

        result = result.reset_index(drop=True)

        if len(result) != len(source):
            raise ValueError(f"Eksik sonuç: {path}")

        if not result["label"].equals(source["label"]):
            raise ValueError(f"Etiket uyuşmazlığı: {path}")

        if not result["text"].fillna("").astype(str).equals(
            source["text"].fillna("").astype(str)
        ):
            raise ValueError(f"Yorum uyuşmazlığı: {path}")

        data[model] = result["prediction"]
        data[f"{model}_hata"] = (
            data[model] != data["gercek_etiket"]
        )

    data["hata_sayisi"] = data[
        [f"{model}_hata" for model in MODELS]
    ].sum(axis=1)

    data["hatali_modeller"] = data.apply(
        lambda row: ", ".join(
            model.upper()
            for model in MODELS
            if row[f"{model}_hata"]
        ),
        axis=1
    )

    return data


def main():
    data = pd.concat([
        load_language(language, display)
        for language, display in LANGUAGES.items()
    ], ignore_index=True)

    print("\nGENEL HATA ANALİZİ")

    for language in LANGUAGES.values():
        subset = data[data["dil"] == language]
        all_wrong = (subset["hata_sayisi"] == 3).sum()

        print(f"\n{language}")
        print(f"Üç modelin de yanıldığı: {all_wrong}")
        print(
            "En az bir modelin yanıldığı:",
            (subset["hata_sayisi"] >= 1).sum()
        )

    # Türkçe nötr yorumların tahmin dağılımı
    neutral = data[
        (data["dil"] == "Türkçe")
        & (data["gercek_etiket"] == "neutral")
    ]

    print("\nTÜRKÇE NÖTR YORUMLAR (1000 YORUM)")

    for model in MODELS:
        print(f"\n{model.upper()}:")
        print(
            neutral[model]
            .value_counts()
            .reindex(LABELS, fill_value=0)
            .to_string()
        )

    # Her model, dil ve gerçek sınıf için
    # 5 yanlış tahmin örneği seç.
    selected = set()

    for language in LANGUAGES.values():
        for label in LABELS:
            for model in MODELS:
                pool = data[
                    (data["dil"] == language)
                    & (data["gercek_etiket"] == label)
                    & (data[f"{model}_hata"])
                ]

                sample = pool.sample(
                    n=min(5, len(pool)),
                    random_state=42
                )
                selected.update(sample.index)

    # Türkçe nötr sınıfında üç modelin
    # birden yanıldığı 15 ek örnek seç.
    pool = neutral[neutral["hata_sayisi"] == 3]

    sample = pool.sample(
        n=min(15, len(pool)),
        random_state=42
    )
    selected.update(sample.index)

    columns = [
        "dil", "yorum_id", "yorum", "gercek_etiket",
        "vader", "bert", "claude",
        "hata_sayisi", "hatali_modeller"
    ]

    examples = data.loc[sorted(selected), columns].copy()
    path = OUTPUT / "hata_ornekleri.csv"
    examples = preserve_reviews(examples, path)
    examples.to_csv(
        path, index=False, encoding="utf-8-sig"
    )

    print(f"\nSeçilen örnek sayısı: {len(examples)}")
    print(f"Kaydedildi: {path}")
    print(f"Korunan inceleme: {examples['aciklama'].ne('').sum()}")
    print("\nHATA ANALİZİ TAMAMLANDI!")


if __name__ == "__main__":
    main()
