"""Reproduce Table 5 from saved predictions; no models or API calls are run."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"positive", "negative", "neutral"}
PAIRS = (("claude", "bert"), ("claude", "vader"), ("bert", "vader"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def load_predictions(language):
    source_path = ROOT / "data" / f"{language.capitalize()}_3000.csv"
    source = read_csv(source_path)
    if len(source) != 3000:
        raise ValueError(f"Expected 3000 source rows: {source_path}")
    files = [source_path]
    correct = {}
    for model in ("vader", "bert", "claude"):
        path = ROOT / "results" / model / f"{language}_{model}.csv"
        rows = read_csv(path)
        files.append(path)
        if rows and "row_id" in rows[0]:
            if sorted(int(row["row_id"]) for row in rows) != list(range(len(source))):
                raise ValueError(f"Invalid or duplicate row IDs: {path}")
            rows.sort(key=lambda row: int(row["row_id"]))
        if len(rows) != len(source):
            raise ValueError(f"Row count mismatch: {path}")
        for row, gold in zip(rows, source):
            if row["text"] != gold["text"] or row["label"] != gold["label"]:
                raise ValueError(f"Source alignment mismatch: {path}")
            if row["prediction"] not in LABELS or row["label"] not in LABELS:
                raise ValueError(f"Invalid label: {path}")
        correct[model] = np.array(
            [row["prediction"] == row["label"] for row in rows], dtype=np.int8
        )
    return correct, files


def paired_bootstrap(first, second, repetitions, seed):
    """Resample row pairs together; report percentile CI in percentage points."""
    difference = first - second
    rng = np.random.default_rng(seed)  # reset for each model pair
    samples = np.empty(repetitions, dtype=float)
    for start in range(0, repetitions, 500):
        count = min(500, repetitions - start)
        indices = rng.integers(0, len(difference), size=(count, len(difference)))
        samples[start:start + count] = difference[indices].mean(axis=1) * 100
    return np.quantile(samples, [0.025, 0.975], method="linear")


def compare(first, second, repetitions=10000, seed=42):
    """McNemar chi-square approximation with continuity correction, 1 df."""
    first_only = int(((first == 1) & (second == 0)).sum())
    second_only = int(((first == 0) & (second == 1)).sum())
    discordant = first_only + second_only
    statistic = max(abs(first_only - second_only) - 1, 0) ** 2 / discordant if discordant else 0.0
    # Survival probability for chi-square with one degree of freedom.
    p_value = math.erfc(math.sqrt(statistic / 2))
    lower, upper = paired_bootstrap(first, second, repetitions, seed)
    return {
        "difference_pp": float((first - second).mean() * 100),
        "ci_lower_pp": float(lower),
        "ci_upper_pp": float(upper),
        "first_only_correct": first_only,
        "second_only_correct": second_only,
        "mcnemar_statistic": statistic,
        "mcnemar_p": p_value,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/comparison/istatistiksel_karsilastirma.csv")
    parser.add_argument("--repetitions", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")
    records, hashes = [], {}
    for language in ("ingilizce", "turkce"):
        correct, paths = load_predictions(language)
        for path in paths:
            hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        for first, second in PAIRS:
            records.append({
                "language": language, "first_model": first, "second_model": second,
                **compare(correct[first], correct[second], args.repetitions, args.seed),
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    metadata = {
        "bootstrap_repetitions": args.repetitions, "seed_per_pair": args.seed,
        "confidence_level": 0.95, "bootstrap": "paired row resampling; percentile; linear quantile",
        "mcnemar": "chi-square approximation; continuity correction; 1 degree of freedom",
        "numpy_version": np.__version__, "input_sha256": hashes,
        "scope": "single saved run and dataset; unadjusted pairwise p-values",
    }
    args.output.with_suffix(".json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
    )
    for record in records:
        print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
