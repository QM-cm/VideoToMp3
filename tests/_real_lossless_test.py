"""真实端到端：lossless + 自定义标题。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Task
from app.core.pipeline import run_pipeline

URL = "https://b23.tv/bdxIc7A"
TMP = os.path.join("data", "tmp")
os.makedirs(TMP, exist_ok=True)

task = Task(id=888, url=URL, custom_title="心似烟火 (DJ版)",
            start_time="00:05", end_time="00:20")

cfg = {"output_dir": os.path.join("data", "output"),
       "quality": "lossless",
       "name_template": "{artist} - {title}.mp3",
       "embed_cover": True}

def on_status(tid, s): print(f"  status -> {s}")
def on_prog(tid, v): print(f"  progress -> {v}", end="\r")

out = run_pipeline(task, cfg, TMP, on_status, on_prog, lambda: False)
print("\n输出文件:", out)
print("文件大小KB:", os.path.getsize(out)//1024)

# 读回 FLAC 标签
from mutagen.flac import FLAC
a = FLAC(out)
print("title:", a.get("title"))
print("artist:", a.get("artist"))
print("封面数:", len(a.pictures))
print("FLAC_E2E_OK")
