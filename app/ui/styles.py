"""蔚蓝档案风主题 QSS：蓝天渐变背景、白色大圆角卡片、深蓝粗体标题、胶囊按钮。

配色：
  天空渐变 #8FD0F5 → #DCEEFB · 深蓝标题 #2456A6 · 主按钮 #3D8BD9 渐变
  卡片白色大圆角 16px、淡蓝描边 · 半透明药丸
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app import constants as C

_QSS = f"""
* {{
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {C.TEXT};
}}
QMainWindow, QDialog {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {C.SKY_TOP}, stop:1 {C.SKY_BOTTOM});
}}
QWidget {{
    background: transparent;
}}

/* ── 白色大圆角卡片（半透明，浮在游戏背景上） ── */
#card {{
    background: rgba(255,255,255,235);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 16px;
}}

/* ── 顶部药丸（半透明白） ── */
#pill {{
    background: {C.PILL_BG};
    border: 1px solid {C.PILL_BORDER};
    border-radius: 14px;
    padding: 4px 12px;
    color: {C.TEXT};
    font-size: 12px;
}}

/* ── 圆形图标按钮（顶部） ── */
#circleBtn {{
    background: {C.PILL_BG};
    border: 1px solid {C.PILL_BORDER};
    border-radius: 18px;
    min-width: 36px; min-height: 36px;
    max-width: 36px; max-height: 36px;
    font-size: 15px;
}}
#circleBtn:hover {{ background: #FFFFFF; }}

/* ── 标题大字（深蓝粗体） ── */
#titleLbl {{
    color: {C.DEEP_BLUE};
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 1px;
}}
#groupTitle {{
    font-size: 14px;
    font-weight: 700;
    color: {C.DEEP_BLUE};
    padding: 2px 0;
}}

/* ── 按钮 ── */
QPushButton {{
    border: none;
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 13px;
}}
QPushButton:focus {{ outline: none; }}

/* 主按钮：游戏风蓝色渐变大圆角 */
#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {C.ACCENT_LIGHT}, stop:1 {C.ACCENT_DARK});
    color: #FFFFFF;
    font-weight: 700;
    font-size: 15px;
    padding: 11px 28px;
    border-radius: 12px;
    border: 1px solid {C.ACCENT_DARK};
}}
#primaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #9CCBF5, stop:1 {C.ACCENT});
}}
#primaryBtn:pressed {{
    background: {C.ACCENT_DARK};
    padding-top: 12px; padding-bottom: 10px;
}}
#primaryBtn:disabled {{ background: #B9D6EE; border-color: #B9D6EE; }}

#secondaryBtn {{
    background: {C.CARD};
    color: {C.ACCENT_DARK};
    border: 1.5px solid {C.ACCENT};
    font-weight: 600;
}}
#secondaryBtn:hover {{ background: {C.INFO_BG}; }}

#ghostBtn {{
    background: transparent;
    color: {C.TEXT_MUTED};
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 12px;
}}
#ghostBtn:hover {{ background: {C.INFO_BG}; color: {C.ACCENT_DARK}; }}

#dangerGhostBtn {{
    background: transparent;
    color: {C.TEXT_MUTED};
    border-radius: 8px;
    padding: 5px 9px;
    font-size: 12px;
}}
#dangerGhostBtn:hover {{ background: {C.DANGER_BG}; color: {C.DANGER}; }}

/* ── 输入控件 ── */
QLineEdit, QTextEdit, QComboBox, QSpinBox {{
    background: {C.CARD};
    border: 1.5px solid {C.INPUT_BORDER};
    border-radius: 10px;
    padding: 7px 11px;
    font-size: 13px;
    color: {C.TEXT};
    selection-background-color: {C.ACCENT};
    selection-color: #FFFFFF;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1.5px solid {C.ACCENT};
}}
QLineEdit:disabled, QTextEdit:disabled {{
    background: #F1F7FC; color: {C.TEXT_MUTED};
}}
QLineEdit::placeholder, QTextEdit::placeholder {{ color: #A8C2D8; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background: {C.CARD};
    border: 1px solid {C.BORDER};
    border-radius: 10px;
    padding: 4px;
    selection-background-color: {C.INFO_BG};
    selection-color: {C.TEXT};
}}

/* ── 复选框 ── */
QCheckBox {{ spacing: 8px; font-size: 13px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 6px;
    border: 1.5px solid {C.INPUT_BORDER}; background: {C.CARD};
}}
QCheckBox::indicator:hover {{ border-color: {C.ACCENT}; }}
QCheckBox::indicator:checked {{
    background: {C.ACCENT}; border-color: {C.ACCENT};
}}

/* ── 表格 ── */
QTableWidget {{
    background: transparent; border: none; gridline-color: transparent;
}}
QTableWidget::item {{ border-bottom: 1px solid #EDF4FA; padding: 2px; }}
QTableWidget::item:selected {{ background: {C.INFO_BG}; color: {C.TEXT}; }}
QTableWidget::item:hover {{ background: #F4F9FE; }}
QHeaderView::section {{
    background: transparent; border: none;
    border-bottom: 2px solid {C.BORDER};
    padding: 8px 6px; color: {C.TEXT_MUTED}; font-size: 12px; font-weight: 700;
}}
QTableCornerButton::section {{ background: transparent; border: none; }}

/* ── 进度条（游戏风蓝色，更纤细精致） ── */
QProgressBar {{
    background: #E4EFF9; border: none; border-radius: 4px; height: 8px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {C.ACCENT_LIGHT}, stop:1 {C.ACCENT});
    border-radius: 4px;
}}

/* ── 滚动条 ── */
QScrollBar:vertical {{ background: transparent; width: 9px; margin: 2px; }}
QScrollBar::handle:vertical {{
    background: #BBD8EE; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {C.ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 9px; margin: 2px; }}
QScrollBar::handle:horizontal {{
    background: #BBD8EE; border-radius: 4px; min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: {C.ACCENT}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── 列表 ── */
QListWidget {{
    background: {C.CARD};
    border: 1.5px solid {C.BORDER};
    border-radius: 12px; padding: 4px;
}}
QListWidget::item {{ padding: 9px 10px; border-radius: 8px; }}
QListWidget::item:hover {{ background: {C.INFO_BG}; }}
QListWidget::item:selected {{ background: {C.INFO_BG}; color: {C.ACCENT_DARK}; }}

QToolTip {{
    background: {C.DEEP_BLUE}; color: #FFFFFF;
    border: none; border-radius: 6px; padding: 5px 9px; font-size: 12px;
}}
"""


def apply_theme(app: QApplication) -> None:
    """应用蔚蓝档案风主题。"""
    app.setStyle("Fusion")
    app.setStyleSheet(_QSS)
