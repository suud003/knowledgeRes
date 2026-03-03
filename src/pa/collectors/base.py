"""采集器基类."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any


class BaseCollector(ABC):
    """数据采集器基类."""

    def __init__(self, name: str, raw_dir: Path) -> None:
        self.name = name
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def collect(self) -> list[dict[str, Any]]:
        """执行数据采集，返回原始数据列表."""
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        """返回数据源类型标识."""
        pass

    def save_raw(self, data: list[dict[str, Any]]) -> Path:
        """保存原始数据到文件."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.name}_{timestamp}.json"
        filepath = self.raw_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "source": self.get_source_type(),
                    "collector": self.name,
                    "collected_at": datetime.now().isoformat(),
                    "count": len(data),
                    "data": data,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        return filepath

    def load_latest_raw(self) -> list[dict[str, Any]] | None:
        """加载最新的原始数据."""
        pattern = f"{self.name}_*.json"
        files = sorted(self.raw_dir.glob(pattern), reverse=True)

        if not files:
            return None

        with open(files[0], "r", encoding="utf-8") as f:
            content = json.load(f)
            return content.get("data", [])
