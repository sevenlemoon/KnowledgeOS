"""数据库迁移脚本：添加新字段和新表。"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pymysql
from app.core.config import settings

# 解析数据库连接信息
url = settings.database_url
# mysql+pymysql://root:ltygxz712@127.0.0.1:3306/bysj?charset=utf8mb4
clean_url = url.split("?")[0]
parts = clean_url.replace("mysql+pymysql://", "").split("@")
user_pass = parts[0].split(":")
host_db = parts[1].split("/")
host_port = host_db[0].split(":")

conn = pymysql.connect(
    host=host_port[0],
    port=int(host_port[1]),
    user=user_pass[0],
    password=user_pass[1],
    database=host_db[1],
    charset="utf8mb4",
)

cursor = conn.cursor()

# 添加新字段（如果不存在）
ALTERS = [
    "ALTER TABLE sys_user ADD COLUMN login_fail_count INT NOT NULL DEFAULT 0",
    "ALTER TABLE sys_user ADD COLUMN locked_until DATETIME NULL",
    "ALTER TABLE sys_user ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0",
    "ALTER TABLE knowledge_base ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0",
    "ALTER TABLE knowledge_comment ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0",
    "ALTER TABLE knowledge_comment ADD COLUMN parent_id INT NULL",
]

for sql in ALTERS:
    try:
        cursor.execute(sql)
        print(f"OK: {sql}")
    except pymysql.err.OperationalError as e:
        if "Duplicate column" in str(e):
            print(f"SKIP (already exists): {sql.split('ADD COLUMN')[1].strip()}")
        else:
            print(f"ERROR: {sql} -> {e}")

# 创建新表
NEW_TABLES = [
    """CREATE TABLE IF NOT EXISTS user_interaction (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        knowledge_id INT NOT NULL,
        action VARCHAR(20) NOT NULL,
        create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_user_knowledge_action (user_id, knowledge_id, action),
        INDEX idx_user (user_id),
        INDEX idx_knowledge (knowledge_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS operation_log (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NULL,
        username VARCHAR(50) NULL,
        operation VARCHAR(50) NOT NULL,
        method VARCHAR(10) NULL,
        path VARCHAR(200) NULL,
        ip VARCHAR(50) NULL,
        status_code INT NULL,
        detail TEXT NULL,
        create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user (user_id),
        INDEX idx_operation (operation),
        INDEX idx_create_time (create_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    """CREATE TABLE IF NOT EXISTS audit_history (
        id INT PRIMARY KEY AUTO_INCREMENT,
        knowledge_id INT NOT NULL,
        auditor_id INT NOT NULL,
        status VARCHAR(20) NOT NULL,
        quality_score DECIMAL(6,2) DEFAULT 0,
        remark VARCHAR(500) NULL,
        create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_knowledge (knowledge_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
]

for sql in NEW_TABLES:
    try:
        cursor.execute(sql)
        table_name = sql.split("TABLE IF NOT EXISTS")[1].split("(")[0].strip()
        print(f"OK: table {table_name}")
    except Exception as e:
        print(f"ERROR: {e}")

# 添加索引
INDEXES = [
    "CREATE INDEX idx_knowledge_status ON knowledge_base (status)",
    "CREATE INDEX idx_knowledge_author ON knowledge_base (author_id)",
    "CREATE INDEX idx_knowledge_category ON knowledge_base (category)",
    "CREATE INDEX idx_points_user ON points_record (user_id)",
]

for sql in INDEXES:
    try:
        cursor.execute(sql)
        print(f"OK: {sql}")
    except pymysql.err.OperationalError as e:
        if "Duplicate key" in str(e):
            print(f"SKIP (index exists): {sql.split('ON')[0].strip()}")
        else:
            print(f"ERROR: {sql} -> {e}")

conn.commit()
cursor.close()
conn.close()
print("\n迁移完成！")
