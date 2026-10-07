"""临时：core 模块静态检查。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.core.filename, app.core.link_extractor, app.core.errors
import app.core.metadata, app.core.downloader, app.core.converter
import app.core.tagger, app.core.pipeline, app.core.worker
from app.core.filename import render_template, resolve_conflict, sanitize_filename
from app.core.link_extractor import extract_urls

urls = extract_urls('看这个 https://www.bilibili.com/video/BV1xx 还有 https://youtube.com/watch?v=123 重复的 https://www.bilibili.com/video/BV1xx')
print('extract_urls:', urls)
assert len(urls) == 2, urls

print('render:', render_template('{artist} - {title}.mp3', artist='薄荷乐队', title='测试'))
print('render no artist:', render_template('{artist} - {title}.mp3', artist='', title='测试'))

print('sanitize:', sanitize_filename('A/B:C*?"<>|  歌曲'))

# 时间计算
from app.models import Task
t = Task(1, 'http://x', start_time='00:02', max_duration='00:03')
from app.core.pipeline import calc_clip
print('calc_clip:', calc_clip(t, video_duration=100))
assert calc_clip(t, 100) == (2.0, 3.0)

# 结束时间裁剪
t2 = Task(2, 'http://x', start_time='00:01', end_time='00:05')
assert calc_clip(t2, 100) == (1.0, 4.0)
print('calc_clip end:', calc_clip(t2, 100))

print('STATIC_OK')
