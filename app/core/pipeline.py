"""单任务流水线编排：解析 → 下载最佳音频 → 转 MP3（裁剪）→ 写标签。

进度约定（0-100）：
  解析 0-5 · 下载 5-45 · 转码 45-90 · 写标签 90-95 · （导入 95-100 为第 4 阶段）
"""

from __future__ import annotations

import os
import re
import urllib.request

from app.core import converter, downloader, metadata, tagger
from app.core.errors import TaskError
from app.core.filename import render_template, resolve_conflict
from app.models import Task

_TIME_RE = re.compile(r"^(?:(\d{1,3}):)?([0-5]?\d):([0-5]\d)$")


def parse_time(text: str) -> float:
    """mm:ss / hh:mm:ss → 秒；空串返回 0；非法返回 -1。"""
    t = (text or "").strip()
    if not t:
        return 0.0
    m = _TIME_RE.match(t)
    if not m:
        return -1.0
    h = int(m.group(1)) if m.group(1) else 0
    return h * 3600 + int(m.group(2)) * 60 + int(m.group(3))


def calc_clip(task: Task, video_duration: float) -> tuple[float, float]:
    """根据 F3 参数计算 (start_sec, duration_sec)。duration=0 表示不裁剪。"""
    start = parse_time(task.start_time)
    if start < 0:
        raise TaskError(f"开始时间「{task.start_time}」格式不正确。")
    end = parse_time(task.end_time)
    if end < 0:
        raise TaskError(f"结束时间「{task.end_time}」格式不正确。")
    max_d = parse_time(task.max_duration)
    if max_d < 0:
        raise TaskError(f"最大时长「{task.max_duration}」格式不正确。")

    if end > 0 and end <= start:
        raise TaskError("结束时间应晚于开始时间。")

    durations: list[float] = []
    if end > 0:
        durations.append(end - start)
    if max_d > 0:
        durations.append(max_d)
    dur = min(durations) if durations else 0.0

    if video_duration > 0 and dur > 0:
        dur = max(0.0, min(dur, video_duration - start))
    return start, dur


def _download_cover(url: str, task_id: int, tmp_dir: str) -> str:
    """下载封面图到临时目录，失败返回空串（不阻断流程）。"""
    if not url:
        return ""
    try:
        ext = ".jpg"
        if url.lower().endswith(".png"):
            ext = ".png"
        path = os.path.join(tmp_dir, f"cover_{task_id}{ext}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r, open(path, "wb") as f:
            f.write(r.read())
        return path if os.path.getsize(path) > 0 else ""
    except OSError:
        return ""


def run_pipeline(task: Task, cfg: dict, tmp_dir: str,
                 on_status, on_progress, cancelled) -> str:
    """执行单任务全流程，返回最终 MP3 路径。失败抛 TaskError。"""

    def emit(s: str):
        on_status(task.id, s)

    # 1) 解析元数据
    emit("parsing")
    info = metadata.extract_metadata(task.url)
    task.title = info["title"]
    task.artist = info["artist"]
    task.duration = info["duration"]
    task.cover_path = _download_cover(info["thumbnail"], task.id, tmp_dir)
    on_progress(task.id, 5)
    if cancelled():
        raise TaskError("任务已取消。", kind="canceled")

    # 2) 计算裁剪参数
    start, dur = calc_clip(task, info["duration"])

    # 3) 下载最佳音频
    emit("downloading")
    src = downloader.download_bestaudio(
        task.url, tmp_dir, task.id,
        progress_cb=lambda p: on_progress(task.id, 5 + int(p * 0.4)))
    if cancelled():
        raise TaskError("任务已取消。", kind="canceled")

    # 4) 转码（按音质档：standard=mp3 128k / high=mp3 320k / lossless=flac）
    emit("converting")
    out_dir = task.save_dir or cfg.get("output_dir", "output")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), out_dir)
    os.makedirs(out_dir, exist_ok=True)

    quality = cfg.get("quality", "high")
    if quality == "lossless":
        fmt, ext, bitrate = "flac", ".flac", 0
    elif quality == "standard":
        fmt, ext, bitrate = "mp3", ".mp3", 128
    else:
        fmt, ext, bitrate = "mp3", ".mp3", 320

    # 自定义标题优先；模板后缀替换为实际格式后缀
    title = task.custom_title or task.title
    template = cfg.get("name_template", "{artist} - {title}.mp3")
    if "." in template:
        template = template[:template.rfind(".")] + ext
    fname = render_template(template, artist=task.artist, title=title)
    fname = resolve_conflict(out_dir, fname)
    out_path = os.path.join(out_dir, fname)

    converter.convert_to_mp3(
        src, out_path,
        bitrate_kbps=bitrate or int(cfg.get("bitrate_kbps", 192)),
        sample_rate=int(cfg.get("sample_rate", 44100)),
        start_sec=start, duration_sec=dur,
        normalize_loudness=bool(cfg.get("normalize_loudness", False)),
        ffmpeg_path=str(cfg.get("ffmpeg_path", "")),
        fmt=fmt)
    on_progress(task.id, 90)
    if cancelled():
        raise TaskError("任务已取消。", kind="canceled")

    # 5) 写标签（FLAC 用 vorbis comment，MP3 用 ID3v2.3）
    emit("tagging")
    tagger.write_tags(
        out_path, fmt=fmt, title=title, artist=task.artist, album="",
        cover_path=task.cover_path if cfg.get("embed_cover", True) else "")
    on_progress(task.id, 95)

    task.output_path = out_path
    task.title = title
    return out_path
