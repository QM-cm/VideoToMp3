"""任务队列表格（F5）：封面/标题/作者/时长/状态/进度/操作。

- 空状态：堆叠显示「粘贴链接开始」插画；
- 操作按钮：重试、打开文件夹、删除（通过信号交给主窗口处理）；
- 第 3 阶段起由真实管线更新状态与进度。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QAbstractItemView, QHBoxLayout, QHeaderView,
                               QLabel, QProgressBar, QStackedWidget,
                               QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)

from app import constants as C
from app.models import Task
from app.ui.widgets import (Card, DangerGhostButton, EmptyState, GhostButton,
                            MutedLabel, StatusChip)

_COVER_SIZE = 52
_ROW_HEIGHT = 62


def format_duration(seconds: float) -> str:
    """秒 → m:ss / mm:ss / h:mm:ss。"""
    sec = int(round(seconds or 0))
    if sec <= 0:
        return "—"
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class TaskTable(Card):
    """任务队列表格。"""

    retry_requested = Signal(int)          # 任务 id
    open_folder_requested = Signal(int)
    delete_requested = Signal(int)
    edit_title_requested = Signal(int)     # 双击标题 / ✎ 按钮
    edit_clip_requested = Signal(int)     # ⏱ 改长度
    save_as_requested = Signal(int)        # 💾 另存为

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks: dict[int, Task] = {}
        self._row_of: dict[int, int] = {}
        self._build_ui()

    # ── UI ──────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        head = QHBoxLayout()
        title = QLabel("任务队列")
        title.setStyleSheet(f"font-size:15px;font-weight:600;color:{C.TEXT};")
        self.count_label = MutedLabel("0 个任务")
        head.addWidget(title)
        head.addSpacing(8)
        head.addWidget(self.count_label)
        head.addStretch(1)
        self.clear_done_btn = GhostButton("清除已完成")
        head.addWidget(self.clear_done_btn)
        root.addLayout(head)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["封面", "标题", "作者", "时长", "状态", "进度", "操作"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(_ROW_HEIGHT)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 76)
        self.table.setColumnWidth(4, 92)
        self.table.setColumnWidth(5, 140)
        self.table.setColumnWidth(6, 230)

        self.empty = EmptyState("🎵", "粘贴链接开始")
        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.table)
        root.addWidget(self.stack, stretch=1)

        self.clear_done_btn.clicked.connect(self._clear_done)

    # ── 数据操作 ────────────────────────────────────────
    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._row_of[task.id] = row
        self._populate_row(row, task)
        self._refresh_empty()

    def remove_task(self, task_id: int) -> None:
        task = self.tasks.pop(task_id, None)
        if task is None:
            return
        row = self._row_of.pop(task_id)
        self.table.removeRow(row)
        # 重排后续行映射
        for tid, r in list(self._row_of.items()):
            if r > row:
                self._row_of[tid] = r - 1
        self._refresh_empty()

    def update_task(self, task_id: int, **fields) -> None:
        task = self.tasks.get(task_id)
        if task is None:
            return
        for k, v in fields.items():
            if hasattr(task, k):
                setattr(task, k, v)
        row = self._row_of.get(task_id)
        if row is not None:
            self._populate_row(row, task)

    def set_status(self, task_id: int, status: str) -> None:
        self.update_task(task_id, status=status)

    def set_progress(self, task_id: int, progress: int) -> None:
        task = self.tasks.get(task_id)
        if task is None:
            return
        task.progress = max(0, min(100, int(progress)))
        row = self._row_of.get(task_id)
        if row is not None:
            bar = self.table.cellWidget(row, 5)
            if isinstance(bar, QProgressBar):
                bar.setValue(task.progress)

    def task_count(self) -> int:
        return len(self.tasks)

    def get_task(self, task_id: int) -> Task | None:
        return self.tasks.get(task_id)

    # ── 行渲染 ──────────────────────────────────────────
    def _populate_row(self, row: int, task: Task) -> None:
        self.table.setCellWidget(row, 0, self._make_cover(task))
        title_lbl = self._make_text(task.display_name(), tooltip=task.url + "\n（双击可改歌名）")
        title_lbl.setStyleSheet(
            f"color:{C.TEXT};font-size:13px;text-decoration:underline;"
            f"text-decoration-style:dotted;text-underline-offset:3px;")
        title_lbl.setCursor(Qt.PointingHandCursor)
        title_lbl.mouseDoubleClickEvent = lambda e, tid=task.id: self.edit_title_requested.emit(tid)
        self.table.setCellWidget(row, 1, title_lbl)
        self.table.setCellWidget(row, 2, self._make_text(task.artist or "—"))
        self.table.setCellWidget(row, 3, self._make_text(format_duration(task.duration), center=True))
        self.table.setCellWidget(row, 4, self._status_chip(task.status))
        self.table.setCellWidget(row, 5, self._make_progress(task.progress))
        self.table.setCellWidget(row, 6, self._make_actions(task))

    @staticmethod
    def _make_cover(task: Task) -> QLabel:
        cover = QLabel("🎵")
        cover.setFixedSize(_COVER_SIZE, _COVER_SIZE)
        cover.setAlignment(Qt.AlignCenter)
        cover.setStyleSheet(
            f"background:{C.MINT_BG};border-radius:10px;font-size:22px;")
        if task.cover_path:
            from PySide6.QtGui import QPixmap
            pm = QPixmap(task.cover_path)
            if not pm.isNull():
                cover.setPixmap(
                    pm.scaled(_COVER_SIZE, _COVER_SIZE,
                              Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                cover.setStyleSheet(
                    f"background:transparent;border-radius:10px;")
        return cover

    @staticmethod
    def _make_text(text: str, tooltip: str = "", center: bool = False) -> QLabel:
        lbl = QLabel(text)
        lbl.setToolTip(tooltip or text)
        lbl.setAlignment(Qt.AlignCenter if center else Qt.AlignVCenter | Qt.AlignLeft)
        lbl.setStyleSheet(f"color:{C.TEXT};font-size:13px;")
        lbl.setWordWrap(False)
        return lbl

    @staticmethod
    def _make_progress(value: int) -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(max(0, min(100, value)))
        bar.setTextVisible(False)
        bar.setFixedWidth(120)
        return bar

    @staticmethod
    def _status_chip(status: str) -> StatusChip:
        return StatusChip(status)

    def _make_actions(self, task: Task) -> QWidget:
        wrap = QWidget()
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        title_btn = GhostButton("✎ 歌名")
        title_btn.setToolTip("修改歌曲标题")
        title_btn.clicked.connect(lambda _=False, tid=task.id: self.edit_title_requested.emit(tid))

        clip_btn = GhostButton("⏱ 长度")
        clip_btn.setToolTip("设置起止时间 / 最大时长")
        clip_btn.clicked.connect(lambda _=False, tid=task.id: self.edit_clip_requested.emit(tid))

        retry = GhostButton("↻")
        retry.setToolTip("重试")
        retry.setEnabled(task.status in (C.STATUS_FAILED, C.STATUS_CANCELED))
        retry.clicked.connect(lambda _=False, tid=task.id: self.retry_requested.emit(tid))

        open_btn = GhostButton("📂")
        open_btn.setToolTip("打开文件所在文件夹")
        open_btn.setEnabled(task.status == C.STATUS_DONE and bool(task.output_path))
        open_btn.clicked.connect(lambda _=False, tid=task.id: self.open_folder_requested.emit(tid))

        save_btn = GhostButton("💾")
        save_btn.setToolTip("另存为到指定文件夹")
        save_btn.setEnabled(task.status == C.STATUS_DONE and bool(task.output_path))
        save_btn.clicked.connect(lambda _=False, tid=task.id: self.save_as_requested.emit(tid))

        delete = DangerGhostButton("✕")
        delete.setToolTip("删除任务")
        delete.clicked.connect(lambda _=False, tid=task.id: self.delete_requested.emit(tid))

        for b in (title_btn, clip_btn, retry, open_btn, save_btn, delete):
            lay.addWidget(b)
        return wrap

    # ── 其他 ────────────────────────────────────────────
    def _refresh_empty(self) -> None:
        has = self.table.rowCount() > 0
        self.stack.setCurrentWidget(self.table if has else self.empty)
        self.count_label.setText(f"{self.table.rowCount()} 个任务")

    def _clear_done(self) -> None:
        """清除已完成/失败/已取消的任务行（保留进行中的）。"""
        finished = [
            tid for tid, t in self.tasks.items()
            if t.status in (C.STATUS_DONE, C.STATUS_FAILED, C.STATUS_CANCELED)
        ]
        for tid in finished:
            self.remove_task(tid)
