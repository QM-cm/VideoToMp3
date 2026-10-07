"""后台 Worker：在 QThreadPool 中执行单任务流水线。"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal

from app.core.errors import TaskError
from app.core.pipeline import run_pipeline
from app.models import Task


class WorkerSignals(QObject):
    status = Signal(int, str)        # task_id, status
    progress = Signal(int, int)      # task_id, progress 0-100
    finished = Signal(int, str)       # task_id, output_path
    failed = Signal(int, str)         # task_id, error_msg


class PipelineWorker(QRunnable):
    """一个任务 = 一个 Worker。"""

    def __init__(self, task: Task, cfg: dict, tmp_dir: str):
        super().__init__()
        self.task = task
        self.cfg = cfg
        self.tmp_dir = tmp_dir
        self.signals = WorkerSignals()
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        try:
            out = run_pipeline(
                self.task, self.cfg, self.tmp_dir,
                on_status=lambda tid, s: self.signals.status.emit(tid, s),
                on_progress=lambda tid, v: self.signals.progress.emit(tid, v),
                cancelled=lambda: self._cancelled,
            )
            self.signals.finished.emit(self.task.id, out or "")
        except TaskError as e:
            if e.kind == "canceled":
                self.signals.status.emit(self.task.id, "canceled")
            else:
                self.signals.failed.emit(self.task.id, e.zh)
        except Exception as e:  # noqa: BLE001
            self.signals.failed.emit(self.task.id, f"未知错误：{e}")
