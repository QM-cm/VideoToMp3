"""把用户给的头像裁成正方形、生成多尺寸 ico。"""
from PIL import Image
import os

SRC = r"C:\Users\Administrator\Documents\xwechat_files\wxid_2rp8sh231dwl22_d14c\temp\RWTemp\2026-10\5707ec427e14d5bddc532c554db9e566\c94bfc16dafca7402afce185e283b6a5.jpg"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "resources", "images")
os.makedirs(OUT_DIR, exist_ok=True)

im = Image.open(SRC).convert("RGBA")
w, h = im.size
print("原图:", w, h)

# 右侧日文约占最右 5%，去掉；人物脸在垂直中下部
left = im.crop((0, 0, int(w * 0.95), h))
lw, lh = left.size
side = min(lw, lh)
# 垂直居中偏下，把脸包进来
x0 = 0
x1 = side
y0 = max(0, (lh - side) // 2 + int(side * 0.08))
y1 = y0 + side
square = left.crop((x0, y0, x1, y1))
square = square.resize((256, 256), Image.LANCZOS)

# 存 png 预览
png_path = os.path.join(OUT_DIR, "icon.png")
square.save(png_path)
print("PNG:", png_path)

# 多尺寸 ico
ico_path = os.path.join(OUT_DIR, "icon.ico")
sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
square.save(ico_path, sizes=sizes)
print("ICO:", ico_path, os.path.getsize(ico_path), "bytes")
