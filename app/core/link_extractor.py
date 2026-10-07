"""链接提取、去重、校验（F1）。UI 层统一调用本模块。"""

from __future__ import annotations

import re

# 提取 http/https 链接：遇空白或中文标点/引号即停止
_URL_RE = re.compile(r"https?://[^\s\u4e00-\u9fff，。；：！？、（）【】《》「」“”‘’\"'<>]+")


def extract_urls(text: str) -> list[str]:
    """从任意文本中提取去重后的 http/https 链接，保持首次出现顺序。"""
    seen: set[str] = set()
    result: list[str] = []
    for url in _URL_RE.findall(text or ""):
        url = url.strip().rstrip(".,;:)")
        if url and url not in seen:
            seen.add(url)
            result.append(url)
    return result


def is_candidate(url: str) -> bool:
    """初步校验：http/https 且域名非空。"""
    if not url:
        return False
    return bool(re.match(r"^https?://[^\s]+\.[^\s]+", url, re.IGNORECASE))
