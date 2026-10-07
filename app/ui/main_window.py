"""主窗口（蔚蓝档案风）：游戏背景图 + 白色半透明卡片浮层。

- 背景图：app/resources/images/bg.jpg（用户本地放置，可替换）；
- 白色半透明遮罩保证文字可读；
- 顶部：圆形 logo + 深蓝大标题 + 药丸状资源栏；
- 中部：链接输入卡片 + 任务表格；底部：游戏风大按钮。

第 2 阶段说明：
- 「开始转换」为界面演示模式（QTimer 模拟进度），第 3 阶段接真实管线。
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QLabel,
                               QMainWindow, QMessageBox, QVBoxLayout, QWidget)
from app import constants as C
from app.config import ConfigStore
from app.core.database import HistoryDB
from app.core.worker import PipelineWorker
from app.models import Task
from app.ui.device_dialog import DeviceDialog
from app.ui.history_dialog import HistoryDialog
from app.ui.link_input_card import LinkInputCard
from app.ui.settings_dialog import SettingsDialog
from app.ui.task_table import TaskTable
from app.ui.widgets import (Card, GhostButton, MutedLabel, PrimaryButton)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TMP_DIR = os.path.join(_PROJECT_ROOT, "data", "tmp")


class BackgroundWidget(QWidget):
    """铺满游戏背景图，叠一层白色半透明遮罩保证控件可读。"""

    def __init__(self, bg_path: str, parent=None):
        super().__init__(parent)
        self._bg = QPixmap(bg_path) if os.path.exists(bg_path) else QPixmap()
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        if not self._bg.isNull():
            scaled = self._bg.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            p.drawPixmap(x, y, scaled)
        # 白色半透明遮罩：游戏氛围保留，控件文字清晰
        p.fillRect(self.rect(), QColor(255, 255, 255, 112))
        super().paintEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigStore()
        self.tasks: dict[int, Task] = {}
        self._url_seen: set[str] = set()
        self._next_id = 1
        self.pool = QThreadPool(self)
        self.workers: dict[int, PipelineWorker] = {}
        self.history_db = HistoryDB()
        self._build_ui()
        self._connect()

    # ── UI ──────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.setWindowTitle(C.APP_NAME)
        bg = BackgroundWidget(C.BG_IMAGE, self)
        self.setCentralWidget(bg)
        root = QVBoxLayout(bg)
        root.setContentsMargins(22, 16, 22, 18)
        root.setSpacing(14)

        root.addLayout(self._build_top_bar())

        # 中部：链接输入在上，任务表格在下（占满宽度）
        self.link_card = LinkInputCard()
        self.table = TaskTable()
        root.addWidget(self.link_card)
        root.addWidget(self.table, stretch=1)

        root.addWidget(self._build_bottom_bar())
        self._refresh_output_label()

    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)

        logo = QLabel("♪")
        logo.setFixedSize(40, 40)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {C.ACCENT_LIGHT},stop:1 {C.DEEP_BLUE});"
            f"color:#FFFFFF;border-radius:20px;font-size:20px;font-weight:800;"
            f"border:2px solid rgba(255,255,255,0.9);")

        title = QLabel(C.APP_NAME)
        title.setObjectName("titleLbl")
        slogan = MutedLabel(C.APP_SLOGAN)

        # 药丸资源栏
        self.output_pill = self._make_pill("📁 输出目录")
        q_label = {"standard": "🎵 普通 128k", "high": "🎵 高频 320k",
                   "lossless": "🎵 无损 FLAC"}.get(self.config.get("quality", "high"),
                                                    "🎵 高频 320k")
        self.bitrate_pill = self._make_pill(q_label)
        self.device_pill = self._make_pill("💾 设备未连接")

        self.history_btn = self._circle_btn("📜")
        self.settings_btn = self._circle_btn("⚙")

        bar.addWidget(logo)
        bar.addSpacing(4)
        bar.addWidget(title)
        bar.addWidget(slogan)
        bar.addStretch(1)
        bar.addWidget(self.output_pill)
        bar.addWidget(self.bitrate_pill)
        bar.addWidget(self.device_pill)
        bar.addSpacing(6)
        bar.addWidget(self.history_btn)
        bar.addWidget(self.settings_btn)
        return bar

    def _build_bottom_bar(self) -> Card:
        wrap = Card()
        bar = QHBoxLayout(wrap)
        bar.setContentsMargins(20, 14, 20, 14)
        bar.setSpacing(12)

        out_label = MutedLabel("保存到")
        self.output_lbl = QLabel("")
        self.output_lbl.setStyleSheet(f"color:{C.TEXT_MUTED};font-size:12px;")
        self.output_lbl.setMaximumWidth(220)

        self.change_btn = GhostButton("浏览…")
        self.change_btn.setToolTip("选择默认保存文件夹")

        q_label = MutedLabel("音质")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["普通 128k", "高频 320k", "无损 FLAC"])
        self.quality_combo.setFixedWidth(120)
        q_map = {"standard": 0, "high": 1, "lossless": 2}
        self.quality_combo.setCurrentIndex(q_map.get(self.config.get("quality", "high"), 1))

        self.start_btn = PrimaryButton("▶ 开始转换")
        self.start_btn.setFixedWidth(160)
        self.start_btn.setMinimumHeight(44)

        bar.addWidget(out_label)
        bar.addWidget(self.output_lbl)
        bar.addWidget(self.change_btn)
        bar.addStretch(1)
        bar.addWidget(q_label)
        bar.addWidget(self.quality_combo)
        bar.addSpacing(6)
        bar.addWidget(self.start_btn)
        return wrap

    def _build_character_card(self) -> Card:
        """右侧角色立绘卡：「今日值班」，放碧蓝档案风格立绘。"""
        card = Card()
        card.setFixedWidth(200)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 14, 12, 14)
        lay.setSpacing(8)

        title = QLabel("今日值班")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color:{C.DEEP_BLUE};font-weight:800;font-size:15px;"
            f"letter-spacing:2px;")

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setStyleSheet("background:transparent;")
        pm = QPixmap(C.CHARACTER_IMAGE)
        if not pm.isNull():
            img.setPixmap(pm.scaled(
                176, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        tip = MutedLabel("素材：蔚蓝档案同人\n个人学习用途")
        tip.setAlignment(Qt.AlignCenter)

        lay.addWidget(title)
        lay.addSpacing(4)
        lay.addWidget(img, stretch=1)
        lay.addWidget(tip)
        return card

    @staticmethod
    def _make_pill(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("pill")
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def _circle_btn(self, text: str) -> GhostButton:
        btn = GhostButton(text)
        btn.setObjectName("circleBtn")
        btn.setFixedSize(36, 36)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    # ── 信号连接 ────────────────────────────────────────
    def _connect(self) -> None:
        self.link_card.add_clicked.connect(self._on_add_clicked)
        self.table.retry_requested.connect(self._on_retry)
        self.table.open_folder_requested.connect(self._open_folder)
        self.table.delete_requested.connect(self._on_delete)
        self.table.edit_title_requested.connect(self._on_edit_title)
        self.table.edit_clip_requested.connect(self._on_edit_clip)
        self.table.save_as_requested.connect(self._on_save_as)
        self.settings_btn.clicked.connect(self._open_settings)
        self.history_btn.clicked.connect(self._open_history)
        self.start_btn.clicked.connect(self._on_start)
        self.change_btn.clicked.connect(self._pick_output_dir)

        self.quality_combo.currentIndexChanged.connect(self._on_quality_changed)

    def _on_quality_changed(self, idx: int) -> None:
        q = ["standard", "high", "lossless"][idx]
        self.config.set("quality", q)
        label = ["🎵 普通 128k", "🎵 高频 320k", "🎵 无损 FLAC"][idx]
        self.bitrate_pill.setText(label)

    def _pick_output_dir(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        start = str(self.config.get("output_dir", "output"))
        if not os.path.isabs(start):
            start = os.path.join(_PROJECT_ROOT, start)
        d = QFileDialog.getExistingDirectory(self, "选择默认保存文件夹", start)
        if d:
            self.config.set("output_dir", d)
            self._refresh_output_label()

    # ── 任务行：改歌名 / 改长度 / 另存为 ──────────────────
    def _on_edit_title(self, task_id: int) -> None:
        from PySide6.QtWidgets import QInputDialog
        task = self.tasks.get(task_id)
        if task is None:
            return
        cur = task.custom_title or task.title
        text, ok = QInputDialog.getText(self, "修改歌名",
            "歌曲标题（留空用视频原标题）：", text=cur)
        if ok:
            task.custom_title = text.strip()
            self.table.update_task(task_id, title=task.custom_title or task.title)

    def _on_edit_clip(self, task_id: int) -> None:
        from PySide6.QtWidgets import QInputDialog
        task = self.tasks.get(task_id)
        if task is None:
            return
        start, ok1 = QInputDialog.getText(self, "修改长度",
            "开始时间 mm:ss（空=从开头）：", text=task.start_time)
        if not ok1:
            return
        end, ok2 = QInputDialog.getText(self, "修改长度",
            "结束时间 mm:ss（空=到结尾）：", text=task.end_time)
        if not ok2:
            return
        mx, ok3 = QInputDialog.getText(self, "修改长度",
            "最大时长 mm:ss（空=不限；与结束时间同时设置取较短）：",
            text=task.max_duration)
        if not ok3:
            return
        task.start_time = start.strip()
        task.end_time = end.strip()
        task.max_duration = mx.strip()

    def _on_save_as(self, task_id: int) -> None:
        import shutil
        from PySide6.QtWidgets import QFileDialog
        task = self.tasks.get(task_id)
        if task is None or not task.output_path or not os.path.exists(task.output_path):
            QMessageBox.warning(self, "另存为", "文件不存在或尚未转换完成。")
            return
        d = QFileDialog.getExistingDirectory(self, "选择保存位置",
                                            os.path.dirname(task.output_path))
        if not d:
            return
        target = os.path.join(d, os.path.basename(task.output_path))
        if os.path.exists(target):
            base, ext = os.path.splitext(target)
            i = 1
            while os.path.exists(target):
                target = f"{base} ({i}){ext}"
                i += 1
        shutil.copy2(task.output_path, target)
        task.save_dir = d
        QMessageBox.information(self, "已保存", f"已复制到：\n{target}")

    # ── 添加 / 操作 ─────────────────────────────────────
    def _on_add_clicked(self, entries: list[dict]) -> None:
        added = 0
        for e in entries:
            url = e["url"]
            if url in self._url_seen:
                continue
            self._url_seen.add(url)
            task = Task(
                id=self._next_id,
                url=url,
                start_time=e.get("start_time", ""),
                end_time=e.get("end_time", ""),
                max_duration=e.get("max_duration", ""),
            )
            self._next_id += 1
            self.tasks[task.id] = task
            self.table.add_task(task)
            added += 1
        self.update_status_text()
        if added == 0:
            QMessageBox.information(self, "提示", "没有新增链接（重复或无效）。")

    def _on_retry(self, task_id: int) -> None:
        task = self.tasks.get(task_id)
        if task is None or task.status not in (C.STATUS_FAILED, C.STATUS_CANCELED):
            return
        task.status = C.STATUS_PENDING
        task.progress = 0
        task.error_msg = ""
        self.table.update_task(task_id, status=task.status, progress=0, error_msg="")
        self.update_status_text()
        self._start_worker(task)

    def _on_delete(self, task_id: int) -> None:
        task = self.tasks.pop(task_id, None)
        if task is None:
            return
        self._url_seen.discard(task.url)
        self.table.remove_task(task_id)
        self.update_status_text()

    def _open_folder(self, task_id: int) -> None:
        task = self.tasks.get(task_id)
        if task is None or not task.output_path:
            return
        folder = os.path.dirname(task.output_path)
        if not os.path.exists(folder):
            QMessageBox.warning(self, "打开失败", f"文件夹不存在：\n{folder}")
            return
        try:
            os.startfile(folder)
        except OSError as exc:
            QMessageBox.warning(self, "打开失败", f"无法打开文件夹：\n{exc}")

    # ── 对话框 ──────────────────────────────────────────
    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.config, self)
        if dlg.exec() == SettingsDialog.Accepted:
            self._refresh_output_label()
            self.update_status_text()

    def _open_history(self) -> None:
        HistoryDialog(self, db=self.history_db).exec()

    def open_device_dialog(self) -> DeviceDialog | None:
        dlg = DeviceDialog(self, music_dir=str(self.config.get("device_music_dir", "MUSIC")))
        if dlg.exec() == DeviceDialog.Accepted:
            return dlg
        return None

    # ── 输出目录显示 ────────────────────────────────────
    def _refresh_output_label(self) -> None:
        out = str(self.config.get("output_dir", "output"))
        if not os.path.isabs(out):
            out = os.path.join(_PROJECT_ROOT, out)
        self.output_lbl.setText(f"…{out[-30:]}" if len(out) > 30 else out)
        self.output_lbl.setToolTip(out)
        self.output_pill.setText("📁 已设置输出目录")

    # ── 状态文字 ────────────────────────────────────────
    def update_status_text(self) -> None:
        active = [t for t in self.tasks.values() if t.status in C.ACTIVE_STATUSES]
        queued = [t for t in self.tasks.values() if t.status in C.QUEUED_STATUSES]
        if active:
            self.device_pill.setText(f"🔥 处理中 · {len(active)} 个")
        elif queued:
            self.device_pill.setText(f"⏳ 等待中 · {len(queued)} 个")
        elif self.tasks:
            self.device_pill.setText("✅ 全部完成")
        else:
            self.device_pill.setText("💾 设备未连接")

    # ── 开始 / 真实管线（第 3 阶段） ─────────────────────
    def _on_start(self) -> None:
        ready = [
            t for t in self.tasks.values()
            if t.status in (C.STATUS_PENDING, C.STATUS_PAUSED,
                            C.STATUS_FAILED, C.STATUS_CANCELED)
        ]
        if not ready:
            QMessageBox.information(self, "提示", "暂无待转换的任务，请先粘贴链接。")
            return
        self.pool.setMaxThreadCount(max(1, int(self.config.get("concurrency", 1))))
        os.makedirs(_TMP_DIR, exist_ok=True)
        for t in ready:
            if t.status in (C.STATUS_FAILED, C.STATUS_CANCELED):
                t.status = C.STATUS_PENDING
                t.progress = 0
                t.error_msg = ""
                self.table.update_task(t.id, status=t.status, progress=0, error_msg="")
            self._start_worker(t)
        self.update_status_text()

    def _start_worker(self, task: Task) -> None:
        if task.id in self.workers:
            return  # 已在运行
        task.status = C.STATUS_PENDING
        task.error_msg = ""
        w = PipelineWorker(task, self.config.as_dict(), _TMP_DIR)
        w.signals.status.connect(self._on_worker_status)
        w.signals.progress.connect(self.table.set_progress)
        w.signals.finished.connect(self._on_worker_finished)
        w.signals.failed.connect(self._on_worker_failed)
        self.workers[task.id] = w
        self.pool.start(w)
        self.update_status_text()

    def _on_worker_status(self, task_id: int, status: str) -> None:
        task = self.tasks.get(task_id)
        if task is None:
            return
        task.status = status
        self.table.update_task(task_id, status=status)
        self.update_status_text()

    def _on_worker_finished(self, task_id: int, output_path: str) -> None:
        task = self.tasks.get(task_id)
        if task is None:
            return
        task.status = C.STATUS_DONE
        task.progress = 100
        task.output_path = output_path
        self.table.update_task(task_id, status=C.STATUS_DONE, progress=100)
        self.workers.pop(task_id, None)
        self.update_status_text()
        self.history_db.add(
            url=task.url, title=task.custom_title or task.title,
            artist=task.artist, output_path=output_path,
            status="done", quality=str(self.config.get("quality", "high")))

    def _on_worker_failed(self, task_id: int, err: str) -> None:
        task = self.tasks.get(task_id)
        if task is None:
            return
        task.status = C.STATUS_FAILED
        task.error_msg = err
        self.table.update_task(task_id, status=C.STATUS_FAILED, error_msg=err)
        self.workers.pop(task_id, None)
        self.update_status_text()
        self.history_db.add(
            url=task.url, title=task.custom_title or task.title,
            artist=task.artist, output_path="", status="failed",
            quality=str(self.config.get("quality", "high")))
        QMessageBox.warning(self, "任务失败", f"{task.url}\n{err}")
