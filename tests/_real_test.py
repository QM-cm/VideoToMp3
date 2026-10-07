"""真实链接实测：解析 → 下载 → 转MP3 → 写标签。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import metadata, downloader, converter, tagger
from app.core.filename import render_template, resolve_conflict
from app.core.pipeline import _download_cover

URL = "https://b23.tv/bdxIc7A"
TMP = os.path.join("data", "tmp")
OUT = os.path.join("data", "output")
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

print("[1] 解析元数据...")
info = metadata.extract_metadata(URL)
print("    标题:", info["title"])
print("    作者:", info["artist"])
print("    时长:", info["duration"], "秒")
print("    站点:", info["extractor"])
print("    封面:", info["thumbnail"][:80])

print("[2] 下载最佳音频...")
src = downloader.download_bestaudio(URL, TMP, 999, progress_cb=lambda p: print(f"\r    进度 {p}%", end="", flush=True))
print(f"\n    下载完成: {src} ({os.path.getsize(src)//1024} KB)")

print("[3] 下载封面...")
cover = _download_cover(info["thumbnail"], 999, TMP)
print("    封面:", cover)

print("[4] 转码 MP3（192k, 44.1kHz）...")
fname = render_template("{artist} - {title}.mp3", artist=info["artist"], title=info["title"])
fname = resolve_conflict(OUT, fname)
out_path = os.path.join(OUT, fname)
converter.convert_to_mp3(src, out_path, bitrate_kbps=192, sample_rate=44100)
print("    输出:", out_path, f"({os.path.getsize(out_path)//1024} KB)")
print("    时长:", round(converter.probe_duration(out_path), 1), "秒")

print("[5] 写入标签...")
tagger.write_mp3_tags(out_path, title=info["title"], artist=info["artist"],
                      album="", cover_path=cover)
tags = tagger.read_mp3_tags(out_path)
print("    标签:", tags)

print("\nREAL_TEST_OK")
print("OUTPUT:", out_path)
