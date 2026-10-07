# 视频转 MP3 助手

粘贴视频链接 → 自动解析 → 下载音频 → 转 MP3/FLAC → 写歌曲标签 → 保存到任意文件夹。
Windows 桌面软件，蔚蓝档案（Blue Archive）风格界面。

## 功能

- **链接解析**：支持 B站、YouTube 等 yt-dlp 支持的站点；自动从多行文本提取链接、去重
- **三档音质**：
  - 普通 128k（MP3，小巧兼容老设备）
  - 高频 320k（MP3，听感接近无损）
  - 无损 FLAC（真无损，文件较大）
- **长度裁剪**：每个任务单独设置开始/结束时间（mm:ss）或最大时长
- **自定义标题**：双击标题或点 ✎ 按钮改成你想要的歌名
- **标签嵌入**：标题、艺术家、封面图自动写入文件（MP3 用 ID3v2.3，FLAC 用 Vorbis）
- **保存位置**：默认目录可在底部「浏览…」选择；完成后单首可 💾 另存为到任意文件夹（含 U盘/MP4）
- **历史记录**：所有转换自动入库，可搜索、重新导出、打开文件夹、删除
- **后台线程**：下载/转码在独立线程，界面不卡死；并发数可在设置中调

## 开发运行

```bash
pip install -r requirements.txt
python main.py
```

## 打包成 exe

```bash
python build.py
```

产物在 `dist/视频转MP3助手/` 目录，双击 `视频转MP3助手.exe` 即可运行。

## 目录结构

```
VideoToMp3/
├── main.py                 # 程序入口
├── app/
│   ├── constants.py        # 配色/状态/默认配置
│   ├── config.py            # config.json 读写
│   ├── models.py            # Task 数据模型
│   ├── core/                # 下载/转码/标签/历史核心逻辑
│   │   ├── errors.py
│   │   ├── link_extractor.py
│   │   ├── filename.py
│   │   ├── metadata.py       # yt-dlp 解析
│   │   ├── downloader.py    # yt-dlp 下载
│   │   ├── converter.py      # ffmpeg 转码
│   │   ├── tagger.py        # ID3v2.3 / FLAC 标签
│   │   ├── pipeline.py      # 单任务流水线
│   │   ├── worker.py        # QThreadPool 后台线程
│   │   └── database.py      # SQLite 历史
│   └── ui/                  # PySide6 界面
├── app/resources/images/   # 背景与角色素材
├── data/
│   ├── tmp/                 # 下载临时文件
│   ├── output/              # 默认输出
│   └── history.db           # 历史数据库
└── tests/                   # 验证脚本
```

## 合规声明

- 仅处理用户主动粘贴、且用户有权下载/保存的公开视频链接
- 不绕过 DRM、付费墙、登录限制、会员限制
- 平台提示需要登录、会员或地区限制时，软件会给出中文提示并停止
- 下载的音频请自行遵守来源平台的版权条款，勿用于商业用途

## 技术栈

Python 3.11+ · PySide6 · yt-dlp · ffmpeg（imageio-ffmpeg 内置）· mutagen · SQLite · PyInstaller
