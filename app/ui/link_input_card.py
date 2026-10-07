"""链接输入卡片（F1 + F3）。

- 多行粘贴自动提取 http/https 链接；
- 一键从剪贴板粘贴；
- 长度调整区：起止时间截取 + 最大时长限制（每个任务单独设置）。
"""

from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QTextEdit, QVBoxLayout, QWidget)

from app import constants as C
from app.core.link_extractor import extract_urls
from app.ui.widgets import Card, GhostButton, MutedLabel, PrimaryButton

# 时间格式：mm:ss 或 hh:mm:ss
_TIME_RE = re.compile(r"^(?:(\d{1,3}):)?([0-5]?\d):([0-5]\d)$")

# 快捷预设：名称, 开始, 结束, 最大时长
_PRESETS: list[tuple[str, str, str, str]] = [
    ("整段", "", "", ""),
    ("前 1 分钟", "00:00", "", "01:00"),
    ("前 3 分钟", "00:00", "", "03:00"),
    ("自定义", "", "", ""),
]


def parse_time(text: str) -> int | None:
    """把 mm:ss / hh:mm:ss 解析为秒；空串返回 None；非法返回 None（由调用方报错）。"""
    t = (text or "").strip()
    if not t:
        return None
    m = _TIME_RE.match(t)
    if not m:
        return None
    hours = int(m.group(1)) if m.group(1) else 0
    minutes = int(m.group(2))
    seconds = int(m.group(3))
    return hours * 3600 + minutes * 60 + seconds


class LinkInputCard(Card):
    """链接输入卡片。"""

    # 参数：list[dict]，每个条目含 url / start_time / end_time / max_duration
    add_clicked = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect()

    # ── UI ──────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        # 标题行
        head = QHBoxLayout()
        title = QLabel("添加链接")
        title.setStyleSheet(
            f"font-size:15px;font-weight:600;color:{C.TEXT};")
        self.paste_btn = GhostButton("📋 从剪贴板粘贴")
        head.addWidget(title)
        head.addStretch(1)
        head.addWidget(self.paste_btn)
        root.addLayout(head)

        # 粘贴区域
        self.url_edit = QTextEdit()
        self.url_edit.setPlaceholderText(
            "粘贴视频链接，支持多行，自动识别其中的 http/https 链接…\n"
            "支持 B站 / YouTube / 抖音 / 快手 等公开视频"
        )
        self.url_edit.setMinimumHeight(56)
        self.url_edit.setMaximumHeight(76)
        root.addWidget(self.url_edit)

        # 长度调整区
        length_box = QWidget()
        length_box.setStyleSheet(
            f"background:rgba(168,216,255,0.25);border-radius:8px;")
        lbox = QHBoxLayout(length_box)
        lbox.setContentsMargins(12, 8, 12, 8)
        lbox.setSpacing(8)

        lbox.addWidget(QLabel("转换长度"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([p[0] for p in _PRESETS])
        self.preset_combo.setFixedWidth(104)
        lbox.addWidget(self.preset_combo)

        lbox.addSpacing(6)
        lbox.addWidget(self._mini_label("开始"))
        self.start_edit = self._time_edit("00:00")
        lbox.addWidget(self.start_edit)

        lbox.addWidget(self._mini_label("结束"))
        self.end_edit = self._time_edit("留空=到结尾")
        lbox.addWidget(self.end_edit)

        lbox.addWidget(self._mini_label("最长"))
        self.max_edit = self._time_edit("留空=不限")
        lbox.addWidget(self.max_edit)

        root.addWidget(length_box)

        # 底部行
        bottom = QHBoxLayout()
        tip = MutedLabel("仅处理你有权下载的内容 · 支持 B站 / YouTube / 抖音 / 快手")
        self.add_btn = PrimaryButton("＋ 添加任务")
        bottom.addWidget(tip)
        bottom.addStretch(1)
        bottom.addWidget(self.add_btn)
        root.addLayout(bottom)

    @staticmethod
    def _mini_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{C.TEXT_MUTED};font-size:12px;")
        return lbl

    @staticmethod
    def _time_edit(placeholder: str) -> QLineEdit:
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setAlignment(Qt.AlignCenter)
        edit.setFixedWidth(110)
        edit.setStyleSheet(
            f"background:{C.CARD};")
        return edit

    # ── 逻辑 ────────────────────────────────────────────
    def _connect(self) -> None:
        self.paste_btn.clicked.connect(self.fill_from_clipboard)
        self.preset_combo.currentIndexChanged.connect(self._apply_preset)
        self.add_btn.clicked.connect(self._emit_add)

    def _apply_preset(self, index: int) -> None:
        if not 0 <= index < len(_PRESETS):
            return
        _, start, end, max_dur = _PRESETS[index]
        if start is None:  # 自定义：保留用户输入
            return
        self.start_edit.setText(start)
        self.end_edit.setText(end)
        self.max_edit.setText(max_dur)

    def fill_from_clipboard(self) -> None:
        """读取系统剪贴板文本并填入输入框（自动提取链接）。"""
        text = QGuiApplication.clipboard().text()
        if not text:
            QMessageBox.information(self, "提示", "剪贴板为空或没有文本内容。")
            return
        urls = extract_urls(text)
        if not urls:
            QMessageBox.information(self, "提示", "剪贴板中未识别到 http/https 链接。")
            return
        self.url_edit.setPlainText("\n".join(urls))

    def _emit_add(self) -> None:
        """收集链接与长度参数，校验后发 add_clicked。"""
        urls = extract_urls(self.url_edit.toPlainText())
        if not urls:
            QMessageBox.warning(self, "无法添加", "未识别到有效链接。\n请粘贴包含 http/https 的链接后再试。")
            return

        start_text = self.start_edit.text().strip()
        end_text = self.end_edit.text().strip()
        max_text = self.max_edit.text().strip()

        start_sec = parse_time(start_text)
        if start_text and start_sec is None:
            QMessageBox.warning(self, "长度设置无效", f"开始时间「{start_text}」格式不正确。\n请使用 mm:ss 或 hh:mm:ss，例如 01:30。")
            return
        end_sec = parse_time(end_text)
        if end_text and end_sec is None:
            QMessageBox.warning(self, "长度设置无效", f"结束时间「{end_text}」格式不正确。\n请使用 mm:ss 或 hh:mm:ss，例如 03:00。")
            return
        max_sec = parse_time(max_text)
        if max_text and max_sec is None:
            QMessageBox.warning(self, "长度设置无效", f"最大时长「{max_text}」格式不正确。\n请使用 mm:ss 或 hh:mm:ss，例如 02:00。")
            return
        if start_sec is not None and end_sec is not None and end_sec <= start_sec:
            QMessageBox.warning(self, "长度设置无效", "结束时间应晚于开始时间。")
            return
        if max_sec is not None and max_sec <= 0:
            QMessageBox.warning(self, "长度设置无效", "最大时长应大于 0。")
            return

        entries = [
            {
                "url": u,
                "start_time": start_text,
                "end_time": end_text,
                "max_duration": max_text,
            }
            for u in urls
        ]
        self.add_clicked.emit(entries)
        self.url_edit.clear()
