"""Evaluate cosine scores against ground truth. No DB/model access or calibration claims.

CSV columns: genuine (0/1), similarity (-1..1), optional latency_ms.
Usage: python scripts/evaluate_similarity.py validation-scores.csv --threshold 0.4
"""
import argparse
import csv
import json
import math
from pathlib import Path


def evaluate(rows, threshold):
    if not 0 <= threshold <= 1: raise ValueError("threshold must be 0..1")
    genuine, impostor, latencies = [], [], []
    for row in rows:
        score = float(row["similarity"])
        if not math.isfinite(score) or not -1 <= score <= 1 or str(row["genuine"]) not in {"0", "1"}:
            raise ValueError("Each row needs genuine=0/1 and finite similarity=-1..1")
        (genuine if str(row["genuine"]) == "1" else impostor).append(score)
        if row.get("latency_ms"):
            value = float(row["latency_ms"])
            if not math.isfinite(value) or value < 0: raise ValueError("Invalid latency")
            latencies.append(value)
    if not genuine or not impostor: raise ValueError("Both genuine and impostor examples are required")
    latencies.sort()
    return {"threshold": threshold, "genuine_pairs": len(genuine), "impostor_pairs": len(impostor),
            "false_acceptance_rate": sum(x >= threshold for x in impostor) / len(impostor),
            "false_rejection_rate": sum(x < threshold for x in genuine) / len(genuine),
            "p50_ms": latencies[math.ceil(.5 * len(latencies)) - 1] if latencies else None,
            "p95_ms": latencies[math.ceil(.95 * len(latencies)) - 1] if latencies else None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path); parser.add_argument("--threshold", type=float, default=.4)
    args = parser.parse_args()
    with args.csv.open(encoding="utf-8-sig", newline="") as source:
        print(json.dumps(evaluate(csv.DictReader(source), args.threshold), indent=2))
