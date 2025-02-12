import json
from pathlib import Path

current_dir = Path(__file__).parent
file_path = current_dir / "matriz_2024_2.json"

with Path.open(file_path, encoding="utf-8") as f:
    matriz = json.load(f)

for obj in matriz:
    obj["subject"] = obj["subject"].upper()
    obj["teacher"] = obj["teacher"].upper()
    obj["day"] = [d.upper() for d in obj["day"]]

with Path.open(file_path, "w", encoding="utf-8") as f:
    json.dump(matriz, f, ensure_ascii=False, indent=4)
