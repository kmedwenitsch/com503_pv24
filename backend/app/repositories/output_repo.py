from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from datetime import date

from ..schemas.output import DailyOutput


class OutputRepository:
    def __init__(self, base_dir: str):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def _path_for_date(self, d: date) -> Path:
        return self.base / f"{d.isoformat()}.json"

    def save(self, d: date, output: DailyOutput) -> Path:
        p = self._path_for_date(d)
        p.write_text(output.model_dump_json(indent=2), encoding="utf-8")
        return p

    def load(self, d: date) -> Optional[DailyOutput]:
        p = self._path_for_date(d)
        if not p.exists():
            return None
        return DailyOutput.model_validate_json(p.read_text(encoding="utf-8"))

    def load_latest(self) -> Optional[DailyOutput]:
        files = sorted(self.base.glob("*.json"))
        if not files:
            return None
        return DailyOutput.model_validate_json(files[-1].read_text(encoding="utf-8"))
