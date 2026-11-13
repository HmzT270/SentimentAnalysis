"""Translate the current Turkish evaluation set locally, preserving rows and labels."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODEL = "Helsinki-NLP/opus-mt-tr-en"
REVISION = "19c65427cc2af5f191337d4899e0348c4af25902"
BATCH_SIZE = 32
NUM_BEAMS = 4
MAX_NEW_TOKENS = 256


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Eksik ceviri modelini indir")
    args = parser.parse_args()
    source = DATA / "Turkce_3000.csv"
    output = DATA / "Turkce_3000_translated.csv"
    checkpoint = DATA / ".translation_progress.json"
    source_hash = sha256(source)
    with source.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 3000 or any(not r["text"].strip() for r in rows):
        raise ValueError("Beklenen gecerli 3000 Turkce metin bulunamadi")
    meta = {"model": MODEL, "revision": REVISION, "source_sha256": source_hash,
            "num_beams": NUM_BEAMS, "max_new_tokens": MAX_NEW_TOKENS}
    translations = []
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text(encoding="utf8"))
        if saved["metadata"] != meta:
            raise ValueError("Ceviri checkpoint'i farkli veri veya ayarlara ait")
        translations = saved["translations"]
        if len(translations) > len(rows) or any(not isinstance(t, str) or not t.strip() for t in translations):
            raise ValueError("Gecersiz ceviri checkpoint'i")

    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=not args.download)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL, revision=REVISION, local_files_only=not args.download)
    model.generation_config.max_length = None
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    limit = model.config.max_position_embeddings
    lengths = [len(tokenizer.encode(row["text"])) for row in rows]
    if max(lengths) > limit:
        raise ValueError(f"En uzun girdi {max(lengths)} token; model siniri {limit}. Metinler kesilmedi.")
    print(f"Model: {MODEL}; cihaz: {device}; devam: {len(translations)}/{len(rows)}", flush=True)

    with torch.inference_mode():
        for start in range(len(translations), len(rows), BATCH_SIZE):
            texts = [row["text"] for row in rows[start:start + BATCH_SIZE]]
            inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=False).to(device)
            generated = model.generate(**inputs, num_beams=NUM_BEAMS, do_sample=False,
                                       max_new_tokens=MAX_NEW_TOKENS)
            for ids in generated:
                # Refuse silently cut output rather than publishing an incomplete translation.
                if model.config.eos_token_id not in ids[1:].tolist():
                    raise ValueError("Ceviri token sinirina ulasti; eksik cikti kaydedilmedi")
            batch = tokenizer.batch_decode(generated, skip_special_tokens=True)
            if any(not t.strip() for t in batch):
                raise ValueError("Bos ceviri uretildi")
            translations.extend(t.strip() for t in batch)
            checkpoint.write_text(json.dumps({"metadata": meta, "translations": translations},
                                             ensure_ascii=False), encoding="utf8")
            print(f"Ceviri: {len(translations)}/{len(rows)}", flush=True)

    if sha256(source) != source_hash:
        raise ValueError("Kaynak veri ceviri sirasinda degisti")
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "label", "text_en"])
        writer.writeheader()
        writer.writerows({**row, "text_en": text_en} for row, text_en in zip(rows, translations))
    temporary.replace(output)
    meta.update({"output_sha256": sha256(output), "rows": len(rows), "device": device,
                 "batch_size": BATCH_SIZE, "input_truncation": False,
                 "max_input_tokens": max(lengths), "do_sample": False,
                 "model_url": f"https://huggingface.co/{MODEL}/tree/{REVISION}",
                 "prepared_date": "2026-11-12", "method": "local machine translation"})
    (ROOT / "archive/source_records/translation_manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    checkpoint.unlink(missing_ok=True)
    print(f"Kaydedildi: {output}", flush=True)


if __name__ == "__main__":
    main()
