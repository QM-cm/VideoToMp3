"""网页版后端：Flask + 复用 core 下载转码逻辑。

本地跑：python web/app.py
默认监听 0.0.0.0:5000，同局域网手机浏览器访问 http://电脑IP:5000
"""
from __future__ import annotations

import os
import sys
import threading
import uuid
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from flask import Flask, jsonify, request, send_file, render_template

from app.core import metadata, downloader, converter, tagger
from app.core.filename import render_template, resolve_conflict, sanitize_filename
from app.core.errors import TaskError
from app.models import Task
from app.core.pipeline import calc_clip, _download_cover

app = Flask(__name__, static_folder="static", template_folder="templates")

TMP = os.path.join(_ROOT, "data", "tmp_web")
OUT = os.path.join(_ROOT, "data", "output_web")
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# 任务表：task_id -> {status, progress, title, artist, error, output_path}
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


def _set(jid: str, **kw):
    with JOBS_LOCK:
        JOBS[jid].update(kw)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parse", methods=["POST"])
def api_parse():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"ok": False, "error": "请输入链接"}), 400
    try:
        info = metadata.extract_metadata(url)
        return jsonify({"ok": True, "info": info})
    except TaskError as e:
        return jsonify({"ok": False, "error": e.zh}), 200


@app.route("/api/convert", methods=["POST"])
def api_convert():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    quality = data.get("quality", "high")  # standard/high/lossless
    start = data.get("start_time", "")
    end = data.get("end_time", "")
    max_dur = data.get("max_duration", "")
    if not url:
        return jsonify({"ok": False, "error": "请输入链接"}), 400

    jid = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[jid] = {"status": "queued", "progress": 0, "error": "",
                     "output_path": "", "title": "", "artist": ""}

    def work():
        try:
            _set(jid, status="parsing", progress=2)
            info = metadata.extract_metadata(url)
            title = info["title"]
            artist = info["artist"]
            _set(jid, title=title, artist=artist, progress=5)

            task = Task(id=hash(jid) % 100000, url=url,
                        start_time=start, end_time=end, max_duration=max_dur)
            task.title = title
            task.artist = artist
            cover = _download_cover(info["thumbnail"], hash(jid) % 100000, TMP)
            task.cover_path = cover

            start_sec, dur = calc_clip(task, info["duration"])

            _set(jid, status="downloading", progress=8)
            src = downloader.download_bestaudio(
                url, TMP, hash(jid) % 100000,
                progress_cb=lambda p: _set(jid, progress=8 + int(p * 0.4)))

            _set(jid, status="converting", progress=55)
            if quality == "lossless":
                fmt, ext, bitrate = "flac", ".flac", 0
            elif quality == "standard":
                fmt, ext, bitrate = "mp3", ".mp3", 128
            else:
                fmt, ext, bitrate = "mp3", ".mp3", 320

            fname = render_template("{artist} - {title}" + ext,
                                    artist=artist, title=title)
            fname = resolve_conflict(OUT, fname)
            out_path = os.path.join(OUT, fname)
            converter.convert_to_mp3(
                src, out_path, bitrate_kbps=bitrate or 192,
                start_sec=start_sec, duration_sec=dur, fmt=fmt)
            _set(jid, progress=92)

            tagger.write_tags(out_path, fmt=fmt, title=title,
                              artist=artist, cover_path=cover)
            _set(jid, status="done", progress=100, output_path=out_path)
        except TaskError as e:
            _set(jid, status="failed", error=e.zh)
        except Exception as e:  # noqa: BLE001
            _set(jid, status="failed", error=f"未知错误：{e}")

    threading.Thread(target=work, daemon=True).start()
    return jsonify({"ok": True, "job_id": jid})


@app.route("/api/status/<jid>")
def api_status(jid):
    with JOBS_LOCK:
        j = JOBS.get(jid)
        if not j:
            return jsonify({"ok": False, "error": "任务不存在"}), 404
        return jsonify({"ok": True, **j})


@app.route("/api/download/<jid>")
def api_download(jid):
    with JOBS_LOCK:
        j = JOBS.get(jid)
    if not j or j.get("status") != "done" or not j.get("output_path"):
        return jsonify({"ok": False, "error": "文件还没准备好"}), 404
    path = j["output_path"]
    if not os.path.exists(path):
        return jsonify({"ok": False, "error": "文件已被清理"}), 404
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  视频转 MP3 网页版已启动")
    print(f"  本机访问:  http://127.0.0.1:{port}")
    print(f"  手机访问:  http://<本机IP>:{port}  (同一 WiFi 下)\n")
    app.run(host="0.0.0.0", port=port, debug=False)
