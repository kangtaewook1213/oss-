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

def save_body_record(selected_date, height, weight, muscle, body_fat):
    """인바디 수치를 검증하고 CSV 파일에 저장한다."""
    try:
        height = float(str(height).strip())
        weight = float(str(weight).strip())
        muscle = float(str(muscle).strip())
        body_fat = float(str(body_fat).strip())
    except (TypeError, ValueError):
        raise ValueError("모든 수치는 숫자로 입력해 주세요.")

    if not all(math.isfinite(v) for v in (height, weight, muscle, body_fat)):
        raise ValueError("유한한 숫자를 입력해 주세요.")

    if not 50 <= height <= 250:
        raise ValueError("키는 50~250 cm 사이여야 합니다.")

    if not 10 <= weight <= 500:
        raise ValueError("체중은 10~500 kg 사이여야 합니다.")

    if not 0 <= muscle <= weight:
        raise ValueError("골격근량은 0 이상이고 체중 이하여야 합니다.")

    if not 0 <= body_fat <= 100:
        raise ValueError("체지방률은 0~100 사이여야 합니다.")

    os.makedirs(os.path.dirname(BODY_TRACKER_CSV), exist_ok=True)

    file_exists = (
        os.path.exists(BODY_TRACKER_CSV)
        and os.path.getsize(BODY_TRACKER_CSV) > 0
    )

    record = {
        "id": next_body_id(),
        "date": selected_date.isoformat(),
        "height_cm": height,
        "weight_kg": weight,
        "skeletal_muscle_mass_kg": muscle,
        "body_fat_percentage": body_fat,
    }

    with open(BODY_TRACKER_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=BODY_TRACKER_HEADER)

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)

    return record