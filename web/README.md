# 网页版使用说明

## 本地运行（自己和手机用）

```bash
cd VideoToMp3
python web/app.py
```

- 电脑浏览器打开：http://127.0.0.1:5000
- **手机**：连同一个 WiFi，浏览器访问 `http://电脑的局域网IP:5000`
  （Windows 查 IP：`ipconfig` 里的 IPv4 地址）

## 部署到公网（让别人打开网址就能用）

GitHub Pages 只能托管静态网页，没有后端跑 yt-dlp/ffmpeg，所以需要两样东西：

1. **前端**：把 `web/templates/index.html` 推到 GitHub Pages（自动有网址）
2. **后端**：把 `web/app.py` 部署到免费 Python 托管平台，例如：
   - Render（render.com）：免费层，连接 GitHub 仓库即可部署
   - Railway / Fly.io 同理

部署时设环境变量 `PORT=10000`，后端会自动监听。前端网页里的 `/api/*` 请求要指向你的后端域名（改 index.html 里 fetch 的 URL）。

## 合规提醒

- 部署到公网后，任何人都能用你的服务器下载视频
- 建议加访问密码（Flask 加个简单的 token 校验）或限制使用
- 仅处理用户有权保存的公开内容，不绕过 DRM / 会员 / 登录限制
