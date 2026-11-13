"""Build balanced, traceable evaluation CSVs without relabelling or model filtering."""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
import unicodedata
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE_RECORDS = ROOT / "archive" / "source_records"
LABELS = ("positive", "negative", "neutral")
SEED = "42"
PER_CLASS = 1000
EN_REV = "4fbd22cd78421f05b1ecdb4fc5725bc7a7bd8f66"
TR_REV = "9647a08a9f0f6ac117d6f79a65578315b27682d9"
SOURCES = {
    "english/test_text.txt": (f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/{EN_REV}/datasets/sentiment/test_text.txt", "09a93a55c63fd93f97485ef7302889d7edb4091cd49733aa37da094f0bfa0675"),
    "english/test_labels.txt": (f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/{EN_REV}/datasets/sentiment/test_labels.txt", "6afb4afe9374d1f983bcf9a7c79b108d0f37fdf020a83f30488309bed215db9d"),
    "english/mapping.txt": (f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/{EN_REV}/datasets/sentiment/mapping.txt", "c0572796fbe261d8ea5fd16c5061076fbba49bc69fc865d6abccaf60daacee24"),
    "turkish/positive.txt": (f"https://raw.githubusercontent.com/sercankulcu/sentiment-analysis-of-tweets-in-Turkish/{TR_REV}/training%20data/positive.txt", "67c938b1da2345bc8ef40f607330f434b642bf3f9176642261e025458029f28d"),
    "turkish/negative.txt": (f"https://raw.githubusercontent.com/sercankulcu/sentiment-analysis-of-tweets-in-Turkish/{TR_REV}/training%20data/negative.txt", "d8e8680470fde6d5d83397e7a4d1bd92f81be62b9df12307c96dd6c16a67ede2"),
    "turkish/notr.txt": (f"https://raw.githubusercontent.com/sercankulcu/sentiment-analysis-of-tweets-in-Turkish/{TR_REV}/training%20data/notr.txt", "a8f0c1da85df82eeedb289896b3c147f858dd704efdbc82e86334f9e9eba78e6"),
}
TURKISH_CSV_HASHES = {
    "positive": "815d1fa345f2fb6de6c4a626281c3c45980777d5a3af7d17b97c2ce48040717d",
    "negative": "84acafca6eb89a7e359c33f4f7dc6476e5deef0258b15d1e3b154f1886f3593c",
    "notr": "e481523b4eb12684390c6f726a675c128a0313c4a78172e64b5b17c38c03e00b",
}
ENGLISH_CSV_HASHES = {
    "ingilizce_tum.csv": "de505ef30ee591592e1f5d4cd42854455ff402505d4ae811fe095ce16f368a0a",
}


ENGLISH_LABEL_MAP = {"0": "negative", "1": "neutral", "2": "positive"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def load_raw(download=False):
    english_paths = {name: SOURCE_RECORDS / "raw/english" / name for name in ENGLISH_CSV_HASHES}
    if any(not path.exists() for path in english_paths.values()):
        if not download:
            raise FileNotFoundError("Ingilizce ham CSV eksik; --download ile calistirin")
        original = {}
        for name, (url, expected) in SOURCES.items():
            if not name.startswith("english/"):
                continue
            with urlopen(url, timeout=90) as response:
                content = response.read()
            if digest(content) != expected:
                raise ValueError(f"Kaynak SHA256 uyusmuyor: {name}")
            original[Path(name).name] = content.decode("utf-8-sig").splitlines()
        mapping = dict(line.split("\t") for line in original["mapping.txt"])
        if mapping != ENGLISH_LABEL_MAP:
            raise ValueError("Ingilizce kaynak etiket eslemesi degisti")
        if len(original["test_text.txt"]) != len(original["test_labels.txt"]):
            raise ValueError("TweetEval metin/etiket sayilari farkli")
        converted = {
            "ingilizce_tum.csv": csv_bytes([
                {"text": text.strip(), "label": mapping[label]}
                for text, label in zip(original["test_text.txt"], original["test_labels.txt"])
            ], ["text", "label"]),
        }
        for name, content in converted.items():
            if digest(content) != ENGLISH_CSV_HASHES[name]:
                raise ValueError(f"CSV donusumu SHA256 uyusmuyor: {name}")
        for name, content in converted.items():
            path = english_paths[name]
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    for name, path in english_paths.items():
        if digest(path.read_bytes()) != ENGLISH_CSV_HASHES[name]:
            raise ValueError(f"Yerel kaynak degistirilmis: {path}")
    for name, (url, expected) in SOURCES.items():
        if name.startswith("english/"):
            continue
        path = SOURCE_RECORDS / "raw" / name
        turkish = name.startswith("turkish/")
        if turkish:
            path = path.with_suffix(".csv")
        local_expected = TURKISH_CSV_HASHES[path.stem] if turkish else expected
        if not path.exists():
            if not download:
                raise FileNotFoundError(f"{path}: once --download ile calistirin")
            with urlopen(url, timeout=90) as response:
                content = response.read()
            if digest(content) != expected:
                raise ValueError(f"Kaynak SHA256 uyusmuyor: {name}")
            if turkish:
                label = "neutral" if path.stem == "notr" else path.stem
                content = csv_bytes([
                    {"text": text.strip(), "label": label}
                    for text in content.decode("utf-8-sig").splitlines()
                ], ["text", "label"])
            if digest(content) != local_expected:
                raise ValueError(f"CSV donusumu SHA256 uyusmuyor: {name}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        if digest(path.read_bytes()) != local_expected:
            raise ValueError(f"Yerel kaynak degistirilmis: {name}")


def candidates():
    label_codes = {label: code for code, label in ENGLISH_LABEL_MAP.items()}
    with (SOURCE_RECORDS / "raw/english/ingilizce_tum.csv").open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["text", "label"]:
            raise ValueError("Ingilizce ham CSV sutunlari gecersiz")
        english = [{"text": row["text"].strip(), "label": row["label"], "source_row": i,
                    "source_label": label_codes[row["label"]], "source_dataset": "TweetEval/sentiment", "source_split": "test"}
                   for i, row in enumerate(reader)]
    turkish = []
    for filename, label in [("positive.txt", "positive"), ("negative.txt", "negative"), ("notr.txt", "neutral")]:
        path = (SOURCE_RECORDS / "raw/turkish" / filename).with_suffix(".csv")
        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != ["text", "label"]:
                raise ValueError(f"Gecersiz CSV sutunlari: {path}")
            rows = list(reader)
        for i, row in enumerate(rows):
            if row["label"] != label:
                raise ValueError(f"Gecersiz kaynak etiketi: {path}, satir {i}")
            turkish.append({"text": row["text"].strip(), "label": label, "source_row": i,
                            "source_label": filename.removesuffix(".txt"),
                            "source_dataset": "sercankulcu/turkish-tweets", "source_split": filename})
    return {"Ingilizce": english, "Turkce": turkish}


def select(rows, language):
    groups = defaultdict(list)
    for row in rows:
        groups[canonical(row["text"])].append(row)
    stats = {"source_rows": len(rows), "source_labels": dict(Counter(r["label"] for r in rows)),
             "empty_removed": 0, "conflicting_rows_removed": 0, "duplicates_removed": 0,
             "outside_three_classes_removed": 0}
    clean = []
    for key, group in groups.items():
        if not key:
            stats["empty_removed"] += len(group)
        elif len({r["label"] for r in group}) > 1:
            stats["conflicting_rows_removed"] += len(group)
        elif group[0]["label"] not in LABELS:
            stats["outside_three_classes_removed"] += len(group)
        else:
            clean.append(group[0])
            stats["duplicates_removed"] += len(group) - 1
    stats["eligible_labels"] = dict(Counter(r["label"] for r in clean))
    chosen = []
    for label in LABELS:
        pool = [r for r in clean if r["label"] == label]
        if len(pool) < PER_CLASS:
            raise ValueError(f"{language}/{label}: yalnizca {len(pool)} uygun ornek")
        pool.sort(key=lambda r: digest(f"{SEED}|select|{language}|{canonical(r['text'])}".encode("utf8")))
        chosen.extend(pool[:PER_CLASS])
    chosen.sort(key=lambda r: digest(f"{SEED}|order|{language}|{canonical(r['text'])}".encode("utf8")))
    assert len(chosen) == 3000 and len({canonical(r["text"]) for r in chosen}) == 3000
    assert Counter(r["label"] for r in chosen) == Counter({label: PER_CLASS for label in LABELS})
    return chosen, stats


def csv_bytes(rows, columns):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8-sig")


def archive_previous():
    # Check every absolute target before any deletion; only project data/results files.
    old = list(DATA.glob("*_3000*.csv")) + list((ROOT / "results").rglob("*"))
    old = [p for p in old if p.is_file()]
    for path in old:
        resolved = path.resolve()
        if not (resolved.is_relative_to(DATA.resolve()) or resolved.is_relative_to((ROOT / "results").resolve())):
            raise ValueError(f"Proje disina cikan yol: {path}")
    if not old:
        return None
    fingerprint = digest(b"".join(p.read_bytes() for p in sorted(old)))[:12]
    archive = ROOT / "archive" / f"previous-datasets-{fingerprint}.zip"
    archive.parent.mkdir(exist_ok=True)
    if archive.exists():
        raise FileExistsError(f"Arsiv zaten var: {archive}")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in old:
            z.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Arsiv dogrulanamadi; eski dosyalar korunuyor")
        for path in old:
            if z.read(path.relative_to(ROOT).as_posix()) != path.read_bytes():
                raise ValueError("Arsiv icerigi uyusmuyor; eski dosyalar korunuyor")
    for path in old:
        path.unlink()
    return archive.relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Eksik sabit surum kaynaklarini indir")
    parser.add_argument("--replace", action="store_true", help="Farkli eski CSV ve sonuclari once arsivle")
    args = parser.parse_args()
    load_raw(args.download)
    outputs = {}
    info = {}
    source_rows = candidates()
    for language, rows in source_rows.items():
        selected, stats = select(rows, language)
        path = DATA / f"{language}_3000.csv"
        outputs[path] = csv_bytes(selected, ["text", "label"])
        provenance = [{"row_id": i, **r, "text_sha256": digest(r["text"].encode("utf8"))}
                      for i, r in enumerate(selected)]
        outputs[SOURCE_RECORDS / "provenance" / f"{language}_3000.csv"] = csv_bytes(provenance, [
            "row_id", "source_dataset", "source_split", "source_row", "source_label", "label", "text_sha256"])
        info[language] = {**stats, "selected_labels": dict(Counter(r["label"] for r in selected)),
                          "output_sha256": digest(outputs[path])}
    different = any(p.exists() and p.read_bytes() != b for p, b in outputs.items())
    if different and not args.replace:
        raise SystemExit("Mevcut veri farkli. Arsivleyip degistirmek icin --replace kullanin.")
    archive = archive_previous() if different else None
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    # CSV views retain source order; original remote TXT hashes stay in the manifest.
    raw_csv_views = {SOURCE_RECORDS / "raw/turkish/turkce_tum.csv": source_rows["Turkce"]}
    for filename in ("positive", "negative", "notr"):
        raw_csv_views[SOURCE_RECORDS / "raw/turkish" / f"{filename}.csv"] = [
            row for row in source_rows["Turkce"] if row["source_split"] == f"{filename}.txt"
        ]
    for filename, label in [("positive", "positive"), ("negative", "negative"), ("notr", "neutral")]:
        raw_csv_views[SOURCE_RECORDS / "raw/english" / f"{filename}.csv"] = [
            row for row in source_rows["Ingilizce"] if row["label"] == label
        ]
    for path, rows in raw_csv_views.items():
        path.write_bytes(csv_bytes(rows, ["text", "label"]))
    manifest_path = SOURCE_RECORDS / "dataset_manifest.json"
    manifest = {"version": "sentiment-social-v1", "prepared_date": "2026-11-12", "seed": SEED,
                "sampling": "SHA256 ranking; 1000 per class; separate SHA256 row shuffle",
                "labels_changed": False, "selection_uses_model_predictions": False,
                "english_revision": EN_REV, "turkish_revision": TR_REV,
                "sources": {name: {"url": url, "sha256": sha, **(
                    {"local_path": str(Path(name).with_suffix(".csv")).replace("\\", "/"),
                     "local_sha256": TURKISH_CSV_HASHES[Path(name).stem]}
                    if name.startswith("turkish/") else {
                        "local_path": "english/ingilizce_tum.csv",
                        "local_sha256": ENGLISH_CSV_HASHES["ingilizce_tum.csv"]}
                )} for name, (url, sha) in SOURCES.items()},
                "english_label_mapping": ENGLISH_LABEL_MAP,
                "datasets": info}
    if manifest_path.exists():
        old_manifest = json.loads(manifest_path.read_text(encoding="utf8"))
        archive = archive or old_manifest.get("previous_data_archive")
    manifest["previous_data_archive"] = archive
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
