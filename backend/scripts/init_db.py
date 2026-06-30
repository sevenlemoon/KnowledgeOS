import sys
from pathlib import Path

import pymysql
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings
from app.db.session import engine
from app.models import Base
from app.services.points import ensure_default_configs, ensure_init_admin


conn = pymysql.connect(
    host=settings.mysql_host,
    port=settings.mysql_port,
    user=settings.mysql_user,
    password=settings.mysql_password,
)
with conn.cursor() as cursor:
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {settings.mysql_db} "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
conn.close()

Base.metadata.create_all(bind=engine)
with Session(engine) as db:
    ensure_default_configs(db)
    ensure_init_admin(db)

print("database initialized")
