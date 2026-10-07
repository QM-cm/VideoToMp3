"""数据模型：Task 任务对象。第 3/4/5 阶段会在此基础上扩展字段与方法。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """一个下载转换任务。id 由主窗口分配，全局自增。"""

    id: int
    url: str
    title: str = ""
    artist: str = ""
    album: str = ""
    duration: float = 0.0            # 视频总时长（秒）
    cover_path: str = ""             # 封面本地路径（第 3 阶段写入）
    start_time: str = ""             # 起止时间截取起点，mm:ss 或 hh:mm:ss，空=从开头
    end_time: str = ""               # 截取终点，空=到结尾
    max_duration: str = ""           # 最大时长限制，空=不限
    status: str = "pending"          # 见 constants.STATUS_*
    progress: int = 0                # 0-100
    output_path: str = ""            # 最终音频文件路径
    device_path: str = ""            # 设备复制路径
    error_msg: str = ""              # 失败原因（中文）
    custom_title: str = ""           # 用户自定义歌曲名，空=用视频原标题
    save_dir: str = ""               # 用户手动指定的保存目录，空=用默认输出目录

    def display_name(self) -> str:
        return self.custom_title or self.title or self.url

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "cover_path": self.cover_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "max_duration": self.max_duration,
            "status": self.status,
            "progress": self.progress,
            "output_path": self.output_path,
            "device_path": self.device_path,
            "error_msg": self.error_msg,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in allowed})
