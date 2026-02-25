import csv
import json
import os
from typing import Dict, List


def load_metrics(report_path: str = "evaluation/metrics.json") -> Dict[str, object]:
    if not os.path.exists(report_path):
        return {}
    with open(report_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_error_samples(csv_path: str = "evaluation/error_samples.csv") -> List[Dict[str, object]]:
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)
