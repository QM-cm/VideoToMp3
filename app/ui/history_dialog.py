"""历史记录窗口（F6）：SQLite 真实数据。

- 搜索框实时过滤（标题/作者/链接）；
- 操作：打开文件夹、重新导出（复制到自选目录）、删除单条；
- 空状态显示「暂无历史记录」。
"""

from __future__ import annotations

import os
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout,
                               QHeaderView, QLineEdit, QMessageBox,
                               QPushButton, QStackedWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QFileDialog)

from app import constants as C
from app.core.database import HistoryDB
from app.ui.widgets import EmptyState, GhostButton, MutedLabel


class HistoryDialog(QDialog):
    def __init__(self, parent=None, db: HistoryDB | None = None):
        super().__init__(parent)
        self.db = db or HistoryDB()
        self.setWindowTitle("历史记录")
        self.setMinimumSize(860, 520)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        top = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索标题 / 作者 / 链接…")
        self.search_edit.setFixedWidth(340)
        refresh_btn = GhostButton("↻ 刷新")
        clear_btn = GhostButton("🗑 清空全部")
        top.addWidget(self.search_edit)
        top.addWidget(refresh_btn)
        top.addWidget(clear_btn)
        top.addStretch(1)
        self.count_lbl = MutedLabel("0 条")
        top.addWidget(self.count_lbl)
        root.addLayout(top)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["时间", "标题", "作者", "音质", "状态", "操作"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(2, 140)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 200)

        self.empty = EmptyState("🗂️", "暂无历史记录")
        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.table)
        root.addWidget(self.stack, stretch=1)

        refresh_btn.clicked.connect(self.refresh)
        self.search_edit.textChanged.connect(self.refresh)
        clear_btn.clicked.connect(self._clear_all)

    # ── 数据 ────────────────────────────────────────────
    def refresh(self) -> None:
        records = self.db.search(self.search_edit.text())
        self.count_lbl.setText(f"{len(records)} 条")
        self.table.setRowCount(0)
        if not records:
            self.stack.setCurrentWidget(self.empty)
            return
        self.stack.setCurrentWidget(self.table)
        for r in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)
            self.table.setItem(row, 0, QTableWidgetItem(r.get("created_at", "")))
            self.table.setItem(row, 1, QTableWidgetItem(r.get("title", "") or "—"))
            self.table.setItem(row, 2, QTableWidgetItem(r.get("artist", "") or "—"))
            self.table.setItem(row, 3, QTableWidgetItem(r.get("quality", "")))
            status = "✅ 完成" if r.get("status") == "done" else "❌ 失败"
            self.table.setItem(row, 4, QTableWidgetItem(status))
            self.table.setCellWidget(row, 5, self._actions(r))

    def _actions(self, record: dict) -> QWidget:  # type: ignore[name-defined]
        wrap = QPushButton()  # placeholder, replaced below
        from PySide6.QtWidgets import QWidget
        wrap = QWidget()
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(2, 0, 2, 0)
        lay.setSpacing(4)

        rid = record["id"]
        path = record.get("output_path", "")
        done = bool(path) and os.path.exists(path)

        open_btn = GhostButton("📂 打开")
        open_btn.setEnabled(done)
        open_btn.clicked.connect(lambda _=False, p=path: self._open(p))

        export_btn = GhostButton("💾 导出")
        export_btn.setEnabled(done)
        export_btn.clicked.connect(lambda _=False, p=path: self._export(p))

        del_btn = GhostButton("✕ 删除")
        del_btn.clicked.connect(lambda _=False, i=rid: self._delete(i))

        for b in (open_btn, export_btn, del_btn):
            lay.addWidget(b)
        return wrap

    @staticmethod
    def _open(path: str) -> None:
        if os.path.exists(path):
            os.startfile(os.path.dirname(path))

    def _export(self, src: str) -> None:
        d = QFileDialog.getExistingDirectory(self, "导出到文件夹")
        if not d:
            return
        target = os.path.join(d, os.path.basename(src))
        if os.path.exists(target):
            base, ext = os.path.splitext(target)
            i = 1
            while os.path.exists(target):
                target = f"{base} ({i}){ext}"
                i += 1
        shutil.copy2(src, target)
        QMessageBox.information(self, "已导出", f"已复制到：\n{target}")

    def _delete(self, record_id: int) -> None:
        self.db.delete(record_id)
        self.refresh()

    def _clear_all(self) -> None:
        if QMessageBox.question(
                self, "清空历史", "确定要清空全部历史记录吗？（不删除已导出的文件）"
        ) != QMessageBox.Yes:
            return
        self.db.clear_all()
        self.refresh()
