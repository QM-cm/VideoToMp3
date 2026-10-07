"""yt-dlp 封装：下载最佳音频流（F4）。"""

from __future__ import annotations

import os
from typing import Callable

from app.core.errors import TaskError
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError


def download_bestaudio(url: str, tmp_dir: str, task_id: int,
                       progress_cb: Callable[[int], None] | None = None) -> str:
    """下载最佳音频到临时目录，返回下载的本地文件路径。

    progress_cb(0-100) 实时回报下载进度。
    """
    os.makedirs(tmp_dir, exist_ok=True)
    out_tmpl = os.path.join(tmp_dir, f"task_{task_id}.%(ext)s")

    def hook(d: dict):
        if progress_cb is None:
            return
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0) or 0
            if total:
                progress_cb(min(99, int(downloaded / total * 100)))
        elif d.get("status") == "finished":
            progress_cb(100)

    opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "noprogress": True,
        "progress_hooks": [hook],
    }

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
    except (DownloadError, ExtractorError, OSError) as e:
        msg = str(e).lower()
        if "no space" in msg or "disk" in msg:
            raise TaskError("磁盘空间不足，无法下载。", kind="disk_full") from e
        if "timed out" in msg or "network" in msg or "connection" in msg:
            raise TaskError("网络连接失败或超时。", kind="network") from e
        raise TaskError(f"下载失败：{str(e)[:120]}", kind="unknown") from e

    if not path or not os.path.exists(path):
        raise TaskError("下载完成但未找到文件。", kind="unknown")
    return path
