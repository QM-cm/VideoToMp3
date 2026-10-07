"""离屏冒烟：确认主窗口无 import 错误、能正常渲染。"""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()

# 添加几个演示任务（不启动真实下载）
from app.models import Task
from app import constants as C
for i in range(3):
    t = Task(id=i+1, url=f"https://example.com/video{i+1}",
             title=f"示例歌曲 {i+1}", artist="示例艺术家", duration=200+i*30)
    w.tasks[t.id] = t
    w.table.add_task(t)

# 状态变更
w.table.update_task(1, status=C.STATUS_DOWNLOADING, progress=40)
w.table.update_task(2, status=C.STATUS_DONE, progress=100)
w.table.update_task(3, status=C.STATUS_FAILED, error_msg="示例错误提示")
w.update_status_text()

os.makedirs("docs/screenshots", exist_ok=True)
app.processEvents()
pix = w.grab()
out = os.path.join("docs", "screenshots", "stage3_smoke.png")
pix.save(out)
print("saved:", out, os.path.getsize(out), "bytes")
print("SMOKE_OK")
