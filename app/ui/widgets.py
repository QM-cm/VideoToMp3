"""通用控件：圆角卡片、主/次/幽灵按钮、状态标签、空状态、图标文本按钮。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QPushButton

from app import constants as C


class Card(QFrame):
    """白色圆角卡片（objectName=card，样式由全局 QSS 提供）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        # 柔和投影，浮在背景上
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(36, 86, 166, 38))
        self.setGraphicsEffect(shadow)


class PrimaryButton(QPushButton):
    """主按钮：薄荷绿底白字。"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("primaryBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(38)


class SecondaryButton(QPushButton):
    """次按钮：白底薄荷绿描边。"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("secondaryBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(34)


class GhostButton(QPushButton):
    """幽灵按钮：默认文字色，悬浮变薄荷绿。"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("ghostBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(28)


class DangerGhostButton(QPushButton):
    """危险幽灵按钮：删除、取消类操作。"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("dangerGhostBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(28)


class StatusChip(QLabel):
    """任务状态小标签：彩色圆角胶囊。"""

    def __init__(self, status: str = "", parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.set_status(status)

    def set_status(self, status: str) -> None:
        label = C.STATUS_LABELS.get(status, status or "—")
        color, bg = C.STATUS_STYLE.get(status, (C.TEXT_MUTED, C.MINT_BG))
        self.setText(label)
        self.setStyleSheet(
            f"background:{bg};color:{color};"
            f"border-radius:9px;padding:2px 10px;font-size:12px;"
        )


class MutedLabel(QLabel):
    """次要说明文字。"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"color:{C.TEXT_MUTED};font-size:12px;")


class EmptyState(QLabel):
    """空状态：简洁插画（字符）+ 提示文字，整体居中。"""

    def __init__(self, icon: str = "🎵", text: str = "粘贴链接开始", parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.set_text(icon, text)

    def set_text(self, icon: str, text: str) -> None:
        self.setText(
            f'<div style="font-size:52px;line-height:1.4;">{icon}</div>'
            f'<div style="color:{C.TEXT_MUTED};font-size:15px;margin-top:6px;">{text}</div>'
        )
