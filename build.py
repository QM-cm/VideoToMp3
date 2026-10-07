"""PyInstaller 打包脚本。运行：python build.py"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = "视频转MP3助手"
ICON = os.path.join(ROOT, "app", "resources", "images", "icon.ico")

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm", "--windowed", "--clean",
    "--name", NAME,
    "--icon", ICON,
    "--paths", ROOT,
    # 界面素材
    "--add-data", os.path.join("app", "resources", "images") + os.pathsep + os.path.join("app", "resources", "images"),
    # yt-dlp 与 ffmpeg 内置二进制
    "--collect-all", "yt_dlp",
    "--collect-all", "imageio_ffmpeg",
    "--collect-all", "mutagen",
    # 隐藏导入
    "--hidden-import", "app.core.worker",
    "--hidden-import", "app.core.pipeline",
    os.path.join(ROOT, "main.py"),
]

print(">>>", " ".join(cmd))
subprocess.run(cmd, cwd=ROOT, check=True)
print(f"\n打包完成：dist/{NAME}/")
