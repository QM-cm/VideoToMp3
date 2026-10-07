"""设备选择对话框（F6 UI 部分）。

- 列出本机磁盘（第 4 阶段将过滤为「可移动磁盘」并显示卷标/容量）；
- 用户选择设备盘符与目标音乐文件夹名（默认 MUSIC）；
- 确定后通过 selected_drive / selected_folder 读取结果。
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QVBoxLayout)

from app import constants as C
from app.ui.widgets import GhostButton, MutedLabel, PrimaryButton, SecondaryButton


def list_drives() -> list[tuple[str, str]]:
    """枚举本机磁盘。返回 [(盘符, 显示文字), ...]。

    第 4 阶段：改为仅返回可移动磁盘，并补充卷标（pywin32 GetVolumeInformation）。
    """
    drives: list[tuple[str, str]] = []
    try:
        import psutil
        for part in psutil.disk_partitions():
            mount = part.mountpoint
            try:
                usage = psutil.disk_usage(mount)
                size_gb = usage.total / (1024 ** 3)
            except OSError:
                size_gb = 0.0
            text = f"{mount}  {size_gb:.1f} GB" if size_gb > 0 else f"{mount}"
            drives.append((mount, text))
    except Exception:  # psutil 缺失时的兜底
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = f"{letter}:\\"
            if os.path.exists(root):
                drives.append((root, root))
    return drives


class DeviceDialog(QDialog):
    """选择导入设备。"""

    def __init__(self, parent=None, music_dir: str = "MUSIC"):
        super().__init__(parent)
        self.selected_drive: str = ""
        self.selected_folder: str = music_dir
        self.setWindowTitle("选择导入设备")
        self.setMinimumWidth(440)
        self._build_ui(music_dir)
        self.refresh()

    def _build_ui(self, music_dir: str) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        title = QLabel("导入到设备")
        title.setStyleSheet(f"font-size:16px;font-weight:600;color:{C.TEXT};")
        root.addWidget(title)

        tip = MutedLabel(
            "MP3 将复制到「设备盘符\\音乐文件夹」下，文件夹不存在会自动创建。")
        root.addWidget(tip)

        self.list = QListWidget()
        self.list.setMinimumHeight(150)
        root.addWidget(self.list)

        row = QHBoxLayout()
        row.addWidget(QLabel("目标文件夹"))
        self.folder_edit = QLineEdit(music_dir)
        self.folder_edit.setPlaceholderText("例如 MUSIC")
        row.addWidget(self.folder_edit, stretch=1)
        root.addLayout(row)

        btn_row = QHBoxLayout()
        self.refresh_btn = SecondaryButton("↻ 刷新")
        self.cancel_btn = GhostButton("取消")
        self.ok_btn = PrimaryButton("确定导入")
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.ok_btn)
        root.addLayout(btn_row)

        self.refresh_btn.clicked.connect(self.refresh)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self._accept)
        self.list.currentRowChanged.connect(lambda _: self.ok_btn.setEnabled(self.list.currentItem() is not None))

    def refresh(self) -> None:
        self.list.clear()
        for mount, text in list_drives():
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, mount)
            self.list.addItem(item)
        self.ok_btn.setEnabled(self.list.count() > 0)

    def _accept(self) -> None:
        item = self.list.currentItem()
        if item is None:
            return
        folder = self.folder_edit.text().strip().strip("\\/")
        if not folder:
            folder = "MUSIC"
        self.selected_drive = item.data(Qt.UserRole)
        self.selected_folder = folder
        self.accept()
