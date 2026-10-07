"""视频转 MP3 助手 · 程序入口。

运行：python main.py
"""

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import constants as C
from app.ui.main_window import MainWindow
from app.ui.styles import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(C.APP_NAME)
    app.setApplicationVersion(C.APP_VERSION)
    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "app", "resources", "images", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    apply_theme(app)

    win = MainWindow()
    win.resize(1100, 780)
    win.setMinimumSize(960, 660)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
