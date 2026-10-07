"""验证 SQLite 历史库写读。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import HistoryDB

db = HistoryDB()
db.add(url="https://example.com/1", title="测试歌名", artist="测试艺术家",
       output_path="C:/fake/test.mp3", status="done", quality="lossless")

records = db.search()
print("记录数:", len(records))
for r in records[-3:]:
    print(" ", r["created_at"], r["title"], r["artist"], r["status"])

# 搜索
hits = db.search("测试")
print("搜索'测试'命中:", len(hits))

# 删一条
if records:
    db.delete(records[0]["id"])
    print("删除后剩余:", db.count())
print("DB_OK")
