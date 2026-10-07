"""JSON 配置读写（ConfigStore）。

- 配置文件位于程序根目录 config.json，缺失时用默认值自动生成。
- 第 5 阶段可在此扩展：字段校验、版本迁移、界面配置项绑定。
"""

from __future__ import annotations

import json
import os
from typing import Any

from app.constants import DEFAULT_CONFIG

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "config.json")


class ConfigStore:
    def __init__(self, path: str = DEFAULT_CONFIG_PATH):
        self.path = path
        self._data: dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        """读取配置；文件不存在或损坏时回退默认值（不覆盖坏文件）。"""
        if not os.path.exists(self.path):
            self.save()
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                # 合并默认值，保证新增配置项也有值
                merged = dict(DEFAULT_CONFIG)
                merged.update(loaded)
                self._data = merged
        except (json.JSONDecodeError, OSError):
            # 配置损坏：保留默认值，等待下次保存时覆盖
            self._data = dict(DEFAULT_CONFIG)

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError:
            # 配置写入失败不阻断程序运行（属于可恢复错误）
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def set_many(self, **kwargs: Any) -> None:
        self._data.update(kwargs)
        self.save()

    def as_dict(self) -> dict[str, Any]:
        return dict(self._data)
