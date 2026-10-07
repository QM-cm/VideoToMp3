"""全局常量：蔚蓝档案风格配色（蓝天 / 海洋 / 白色大圆角卡片）、任务状态、默认配置。"""

# ── 蔚蓝档案风配色 ──────────────────────────────────────
SKY_TOP = "#8FD0F5"        # 背景渐变 · 上（天空蓝）
SKY_BOTTOM = "#DCEEFB"     # 背景渐变 · 下（浅天蓝）
DEEP_BLUE = "#2456A6"      # 标题深蓝（大字）
DEEP_BLUE_DARK = "#1E4E96"
ACCENT = "#3D8BD9"         # 主按钮蓝
ACCENT_DARK = "#2E6FB7"    # 主按钮按下
ACCENT_LIGHT = "#7FBCEE"   # 主按钮悬浮
CARD = "#FFFFFF"            # 卡片背景
CARD_SHADOW = "rgba(46,111,183,0.18)"
PILL_BG = "rgba(255,255,255,0.88)"  # 顶部资源药丸（半透明白）
PILL_BORDER = "rgba(255,255,255,0.95)"

PINK = "#F5A0C0"           # 活动标签粉（进行中）
PINK_BG = "#FDE3EE"
BG = "#EAF5FC"             # 备用浅背景
TEXT = "#2C4A6B"           # 主文字 · 深蓝灰
TEXT_MUTED = "#6E8BA6"     # 次要文字
BORDER = "#CFE3F5"         # 卡片描边
INPUT_BORDER = "#BBD9F0"

SUCCESS = "#4FB783"        # 完成 / 就绪
SUCCESS_BG = "#E2F5EC"
WARN = "#E8A34A"           # 暂停 / 等待
WARN_BG = "#FFF3E0"
DANGER = "#E36B6B"         # 失败 / 删除
DANGER_BG = "#FDECEC"
INFO = "#3D8BD9"           # 通用进行中
INFO_BG = "#E4F1FC"

# 兼容旧引用（部分模块可能引用）
MINT = ACCENT
MINT_LIGHT = ACCENT_LIGHT
MINT_DARK = ACCENT_DARK
MINT_BG = INFO_BG
SKY = "#A8D8FF"
SKY_BG = "#EAF4FF"

# ── 任务状态 ────────────────────────────────────────────
STATUS_PENDING = "pending"
STATUS_PARSING = "parsing"
STATUS_DOWNLOADING = "downloading"
STATUS_CONVERTING = "converting"
STATUS_TAGGING = "tagging"
STATUS_IMPORTING = "importing"
STATUS_DONE = "done"
STATUS_FAILED = "failed"
STATUS_CANCELED = "canceled"
STATUS_PAUSED = "paused"

STATUS_LABELS = {
    STATUS_PENDING: "等待中",
    STATUS_PARSING: "解析中",
    STATUS_DOWNLOADING: "下载中",
    STATUS_CONVERTING: "转码中",
    STATUS_TAGGING: "写标签",
    STATUS_IMPORTING: "导入中",
    STATUS_DONE: "完成",
    STATUS_FAILED: "失败",
    STATUS_CANCELED: "已取消",
    STATUS_PAUSED: "已暂停",
}

# 状态 → (文字色, 背景色)
STATUS_STYLE = {
    STATUS_PENDING: (TEXT_MUTED, INFO_BG),
    STATUS_PARSING: (PINK, PINK_BG),
    STATUS_DOWNLOADING: (PINK, PINK_BG),
    STATUS_CONVERTING: (PINK, PINK_BG),
    STATUS_TAGGING: (PINK, PINK_BG),
    STATUS_IMPORTING: (PINK, PINK_BG),
    STATUS_DONE: (SUCCESS, SUCCESS_BG),
    STATUS_FAILED: (DANGER, DANGER_BG),
    STATUS_CANCELED: (TEXT_MUTED, "#EEF3F8"),
    STATUS_PAUSED: (WARN, WARN_BG),
}

ACTIVE_STATUSES = (STATUS_PARSING, STATUS_DOWNLOADING,
                   STATUS_CONVERTING, STATUS_TAGGING, STATUS_IMPORTING)
QUEUED_STATUSES = (STATUS_PENDING, STATUS_PAUSED)

# ── 应用信息 ────────────────────────────────────────────
APP_NAME = "视频转 MP3 助手"
APP_VERSION = "0.1.0"
APP_SLOGAN = "粘贴链接，一键带走好听的歌"

# ── 默认配置 ────────────────────────────────────────────
DEFAULT_CONFIG = {
    "output_dir": "output",
    "bitrate_kbps": 192,
    "sample_rate": 44100,
    "name_template": "{artist} - {title}.mp3",
    "concurrency": 1,
    "ffmpeg_path": "",
    "auto_import": True,
    "device_music_dir": "MUSIC",
    "embed_cover": True,
    "gen_playlist": False,
    "safe_eject": False,
    "normalize_loudness": False,
    "clipboard_autodetect": True,
}

MAX_CONCURRENCY = 5

# ── 资源路径（用户本地放置的游戏素材） ──────────────────
import os as _os
RESOURCES_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "resources")
IMAGE_DIR = _os.path.join(RESOURCES_DIR, "images")
BG_IMAGE = _os.path.join(IMAGE_DIR, "bg.jpg")           # 窗口背景图
CHARACTER_IMAGE = _os.path.join(IMAGE_DIR, "character.jpg")  # 备用立绘
