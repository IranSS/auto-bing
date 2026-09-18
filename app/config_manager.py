import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = Path(file_path or Path(__file__).resolve().parents[1] / "dados.json")

    def load(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            return {}

        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, data: Dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
