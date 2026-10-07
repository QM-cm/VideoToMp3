"""文件名处理：模板渲染、非法字符清理、重名解决。"""

from __future__ import annotations

import os
import re

# Windows 文件名非法字符
_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]+')
# 首尾禁止的字符
_TRAIL_BAD = " ."


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """清理非法字符与首尾空格/点，限制长度。"""
    if not name:
        return "未命名"
    cleaned = _ILLEGAL_CHARS.sub(" ", str(name))
    cleaned = cleaned.strip().strip(_TRAIL_BAD)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return "未命名"
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned


def render_template(template: str, *, artist: str = "", title: str = "",
                    album: str = "") -> str:
    """渲染命名模板，如 {artist} - {title}.mp3。

    缺 artist 时回退为 title.mp3；缺 title 用占位。
    """
    template = (template or "{artist} - {title}.mp3").strip()
    artist = sanitize_filename(artist) if artist else ""
    title = sanitize_filename(title) if title else "未命名"
    album = sanitize_filename(album) if album else ""

    if "{artist}" in template and not artist:
        # 没有作者：退化为 {title}.mp3
        template = "{title}.mp3"

    name = template.format(artist=artist, title=title, album=album)
    name = sanitize_filename(name, max_len=180)
    return name


def resolve_conflict(directory: str, filename: str) -> str:
    """若目标已存在，自动追加 (1)(2)… 直到不冲突。"""
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
    stem, ext = os.path.splitext(filename)
    i = 1
    while True:
        candidate = f"{stem} ({i}){ext}"
        if not os.path.exists(os.path.join(directory, candidate)):
            return candidate
        i += 1
