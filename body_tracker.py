import csv
import math
import os
from datetime import date

from config import BODY_TRACKER_CSV, BODY_TRACKER_HEADER

def read_body_records():
    """인바디 CSV를 읽어 리스트로 반환한다."""
    if not os.path.exists(BODY_TRACKER_CSV):
        return []

    records = []

    with open(BODY_TRACKER_CSV, "r", newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append({
                    "id": int(row["id"]),
                    "date": row["date"],
                    "height_cm": float(row["height_cm"]),
                    "weight_kg": float(row["weight_kg"]),
                    "skeletal_muscle_mass_kg": float(row["skeletal_muscle_mass_kg"]),
                    "body_fat_percentage": float(row["body_fat_percentage"]),
                })
            except (KeyError, TypeError, ValueError):
                continue

    return records


def next_body_id(records=None):
    if records is None:
        records = read_body_records()

    return max((r["id"] for r in records), default=0) + 1

