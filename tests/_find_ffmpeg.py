import sys, os, subprocess, traceback
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ffmpeg_path.txt")
try:
    import imageio_ffmpeg
    p = imageio_ffmpeg.get_ffmpeg_exe()
    with open(out, "w", encoding="utf-8") as f:
        f.write("PATH=" + p + "\n")
        r = subprocess.run([p, "-version"], capture_output=True, text=True)
        f.write("VERSION=" + (r.stdout.splitlines()[0] if r.stdout else r.stderr[:300]) + "\n")
        f.write("RC=" + str(r.returncode) + "\n")
except Exception:
    with open(out, "w", encoding="utf-8") as f:
        f.write("ERROR\n" + traceback.format_exc())
