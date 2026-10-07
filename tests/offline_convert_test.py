"""离线验证：不联网，用 ffmpeg 生成测试音频 → 转 MP3 → 写标签 → 读回校验。

运行：python tests/offline_convert_test.py
验证点：
  1. ffmpeg 可定位；
  2. 本地 wav 能转成 MP3；
  3. 裁剪（-ss/-t）生效；
  4. ID3v2.3 标签（标题/艺术家/封面）写入并能读回。
"""

from __future__ import annotations

import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.core import converter, tagger  # noqa: E402
from app.core.filename import render_template, resolve_conflict, sanitize_filename  # noqa: E402


def main() -> None:
    work = os.path.join(_ROOT, "data", "test")
    os.makedirs(work, exist_ok=True)

    ffmpeg = converter.find_ffmpeg()
    print(f"[1] ffmpeg 定位: {ffmpeg}")

    # 生成 10 秒测试音频（440Hz 正弦）
    src_wav = os.path.join(work, "test_src.wav")
    subprocess.run(
        [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=10", src_wav],
        check=True)
    print(f"[2] 生成测试音频: {src_wav} ({os.path.getsize(src_wav)} bytes)")

    # 裁剪并转 MP3：从第 2 秒起取 3 秒、192k、44.1kHz
    out_dir = os.path.join(work, "output")
    os.makedirs(out_dir, exist_ok=True)
    fname = render_template("{artist} - {title}.mp3", artist="薄荷乐队", title="测试歌曲")
    fname = resolve_conflict(out_dir, fname)
    out_mp3 = os.path.join(out_dir, fname)
    converter.convert_to_mp3(
        src_wav, out_mp3, bitrate_kbps=192, sample_rate=44100,
        start_sec=2.0, duration_sec=3.0)
    size = os.path.getsize(out_mp3)
    print(f"[3] 转码 MP3: {out_mp3} ({size} bytes)")
    assert size > 1000, "MP3 文件过小"

    # 时长应约 3 秒
    dur = converter.probe_duration(out_mp3)
    print(f"[4] 裁剪后时长: {dur:.2f}s（期望约 3s）")
    assert 2.5 < dur < 3.8, f"裁剪时长异常: {dur}"

    # 写 ID3v2.3 标签（含封面）
    cover = os.path.join(_ROOT, "app", "resources", "images", "character.jpg")
    tagger.write_mp3_tags(
        out_mp3, title="测试歌曲", artist="薄荷乐队", album="测试专辑",
        cover_path=cover if os.path.exists(cover) else "")

    tags = tagger.read_mp3_tags(out_mp3)
    print(f"[5] 读回标签: {tags}")
    assert tags["title"] == "测试歌曲"
    assert tags["artist"] == "薄荷乐队"
    assert tags["album"] == "测试专辑"
    assert tags["has_cover"], "封面未写入"

    # 文件名清理
    dirty = 'A/B:C*?"<>|  歌曲'
    clean = sanitize_filename(dirty)
    print(f"[6] 非法字符清理: {dirty!r} -> {clean!r}")
    assert all(ch not in clean for ch in '\\/:*?"<>|')

    print("\nOFFLINE_TEST_OK")


if __name__ == "__main__":
    main()
