"""快速验证：FLAC 无损输出 + 自定义标题。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import converter, tagger
from app.core.filename import render_template, resolve_conflict

work = os.path.join("data", "test")
os.makedirs(work, exist_ok=True)
ffmpeg = converter.find_ffmpeg()

# 生成 3 秒测试音频
src = os.path.join(work, "src2.wav")
import subprocess
subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=3", src], check=True)

# 转 FLAC
out = os.path.join(work, "out.flac")
converter.convert_to_mp3(src, out, fmt="flac", sample_rate=44100)
print("FLAC 大小:", os.path.getsize(out), "bytes")
assert os.path.getsize(out) > 1000

# 写 FLAC 标签
cover = os.path.join("app", "resources", "images", "character.jpg")
tagger.write_tags(out, fmt="flac", title="我的自定义歌名", artist="测试艺术家",
                  cover_path=cover if os.path.exists(cover) else "")

# 读回 FLAC 标签
from mutagen.flac import FLAC
a = FLAC(out)
print("FLAC title:", a.get("title"))
print("FLAC artist:", a.get("artist"))
print("FLAC 封面数:", len(a.pictures))
assert a.get("title") == ["我的自定义歌名"]
assert len(a.pictures) > 0

# 文件名模板后缀替换
tpl = "{artist} - {title}.mp3"
if "." in tpl:
    tpl2 = tpl[:tpl.rfind(".")] + ".flac"
print("模板后缀替换:", render_template(tpl2, artist="A", title="B"))

print("FLAC_OK")
