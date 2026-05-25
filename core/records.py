import json
import os

RECORDS_FILE = "golf_records.json"


def load_records():
    if not os.path.exists(RECORDS_FILE):
        return {}
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_records(records):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def clear_records():
    if os.path.exists(RECORDS_FILE):
        os.remove(RECORDS_FILE)


def get_key(field_type, weather, num_holes):
    return f"{field_type}_{weather}_{num_holes}"


def is_new_record(field_type, weather, num_holes, total_strokes):
    records = load_records()
    key = get_key(field_type, weather, num_holes)
    if key not in records:
        return True
    return total_strokes < records[key]["strokes"]


def update_record(field_type, weather, num_holes, total_strokes, winner_name):
    records = load_records()
    key = get_key(field_type, weather, num_holes)
    if key not in records or total_strokes < records[key]["strokes"]:
        records[key] = {"strokes": total_strokes, "winner": winner_name}
        save_records(records)
        return True
    return False


def get_record(field_type, weather, num_holes):
    records = load_records()
    return records.get(get_key(field_type, weather, num_holes))
