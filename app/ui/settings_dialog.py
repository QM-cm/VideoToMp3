"""设置对话框（F8）：所有可持久化配置项，保存到 config.json（ConfigStore）。"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFileDialog,
                               QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QScrollArea, QSpinBox, QVBoxLayout, QWidget)

from app import constants as C
from app.config import ConfigStore
from app.ui.widgets import GhostButton, MutedLabel, PrimaryButton, SecondaryButton


class SettingsDialog(QDialog):
    """设置页。"""

    def __init__(self, store: ConfigStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("设置")
        self.setMinimumSize(540, 620)
        self._build_ui()
        self._load_from_store()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 滚动表单区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        body = QWidget()
        body.setObjectName("card")
        form = QFormLayout(body)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        scroll.setWidget(body)
        root.addWidget(scroll, stretch=1)

        # ── 常规 ──
        form.addRow(self._group_title("常规"))
        self.output_dir_edit = QLineEdit()
        output_row = QHBoxLayout()
        output_row.setContentsMargins(0, 0, 0, 0)
        output_row.addWidget(self.output_dir_edit, stretch=1)
        browse_out = GhostButton("浏览…")
        browse_out.clicked.connect(self._browse_output)
        output_row.addWidget(browse_out)
        form.addRow("默认输出目录", output_row)
        form.addRow("", MutedLabel("未插入设备时，MP3 保存到此目录"))

        # ── 转换 ──
        form.addRow(self._group_title("转换"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["128", "192", "320"])
        form.addRow("MP3 比特率 (kbps)", self.bitrate_combo)

        self.rate_combo = QComboBox()
        self.rate_combo.addItems(["44100", "48000"])
        form.addRow("采样率 (Hz)", self.rate_combo)

        self.template_edit = QLineEdit()
        form.addRow("命名模板", self.template_edit)
        form.addRow("", MutedLabel(
            "可用变量：{artist} {title} {album}，例如 {artist} - {title}.mp3"))

        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, C.MAX_CONCURRENCY)
        form.addRow("并发任务数", self.concurrency_spin)

        ffmpeg_row = QHBoxLayout()
        ffmpeg_row.setContentsMargins(0, 0, 0, 0)
        self.ffmpeg_edit = QLineEdit()
        ffmpeg_row.addWidget(self.ffmpeg_edit, stretch=1)
        browse_ff = GhostButton("浏览…")
        browse_ff.clicked.connect(self._browse_ffmpeg)
        ffmpeg_row.addWidget(browse_ff)
        form.addRow("ffmpeg 路径", ffmpeg_row)
        form.addRow("", MutedLabel("留空自动探测（PATH 与常见安装位置）"))

        self.normalize_check = QCheckBox("响度标准化（Loudnorm，播放音量更一致）")
        self.embed_cover_check = QCheckBox("嵌入封面图到 MP3")
        form.addRow("", self.embed_cover_check)
        form.addRow("", self.normalize_check)

        # ── 设备 ──
        form.addRow(self._group_title("设备导入"))
        self.auto_import_check = QCheckBox("转换完成后自动导入设备")
        form.addRow("", self.auto_import_check)
        self.music_dir_edit = QLineEdit()
        form.addRow("设备音乐文件夹名", self.music_dir_edit)
        form.addRow("", MutedLabel("复制到 设备盘符\\该文件夹，例如 MUSIC"))

        self.playlist_check = QCheckBox("生成 .m3u 播放列表")
        self.eject_check = QCheckBox("全部完成后安全弹出设备")
        form.addRow("", self.playlist_check)
        form.addRow("", self.eject_check)

        # ── 其他 ──
        form.addRow(self._group_title("其他"))
        self.clipboard_check = QCheckBox("从剪贴板自动识别链接")
        form.addRow("", self.clipboard_check)

        # 底部按钮
        btns = QHBoxLayout()
        btns.setContentsMargins(24, 14, 24, 18)
        self.save_btn = PrimaryButton("保存")
        self.cancel_btn = GhostButton("取消")
        btns.addStretch(1)
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.save_btn)
        root.addLayout(btns)

        self.save_btn.clicked.connect(self._save)
        self.cancel_btn.clicked.connect(self.reject)

    @staticmethod
    def _group_title(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("groupTitle")
        return lbl

    # ── 读写 ────────────────────────────────────────────
    def _load_from_store(self) -> None:
        s = self.store
        self.output_dir_edit.setText(str(s.get("output_dir", "output")))
        self.bitrate_combo.setCurrentText(str(s.get("bitrate_kbps", 192)))
        self.rate_combo.setCurrentText(str(s.get("sample_rate", 44100)))
        self.template_edit.setText(str(s.get("name_template", "{artist} - {title}.mp3")))
        self.concurrency_spin.setValue(int(s.get("concurrency", 1)))
        self.ffmpeg_edit.setText(str(s.get("ffmpeg_path", "")))
        self.auto_import_check.setChecked(bool(s.get("auto_import", True)))
        self.music_dir_edit.setText(str(s.get("device_music_dir", "MUSIC")))
        self.embed_cover_check.setChecked(bool(s.get("embed_cover", True)))
        self.playlist_check.setChecked(bool(s.get("gen_playlist", False)))
        self.eject_check.setChecked(bool(s.get("safe_eject", False)))
        self.normalize_check.setChecked(bool(s.get("normalize_loudness", False)))
        self.clipboard_check.setChecked(bool(s.get("clipboard_autodetect", True)))

    def _save(self) -> None:
        self.store.set_many(
            output_dir=self.output_dir_edit.text().strip() or "output",
            bitrate_kbps=int(self.bitrate_combo.currentText()),
            sample_rate=int(self.rate_combo.currentText()),
            name_template=self.template_edit.text().strip() or "{artist} - {title}.mp3",
            concurrency=self.concurrency_spin.value(),
            ffmpeg_path=self.ffmpeg_edit.text().strip(),
            auto_import=self.auto_import_check.isChecked(),
            device_music_dir=self.music_dir_edit.text().strip() or "MUSIC",
            embed_cover=self.embed_cover_check.isChecked(),
            gen_playlist=self.playlist_check.isChecked(),
            safe_eject=self.eject_check.isChecked(),
            normalize_loudness=self.normalize_check.isChecked(),
            clipboard_autodetect=self.clipboard_check.isChecked(),
        )
        self.accept()

    def _browse_output(self) -> None:
        start = self.output_dir_edit.text().strip() or os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, "选择输出目录", start)
        if path:
            self.output_dir_edit.setText(path)

    def _browse_ffmpeg(self) -> None:
        start = self.ffmpeg_edit.text().strip() or "C:\\"
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 ffmpeg.exe", start, "ffmpeg (ffmpeg.exe)")
        if path:
            self.ffmpeg_edit.setText(path)
