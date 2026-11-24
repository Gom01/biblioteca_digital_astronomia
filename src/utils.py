import json
from pathlib import Path


def load_json(filename: str | Path) -> list[dict]:
    """Load a list of dictionaries from a JSON file."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def save_to_json(data: list[dict], filename: str | Path) -> None:
    """Save a list of dictionaries to a JSON file, creating the folder if needed."""
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
