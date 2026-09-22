import os

import pymysql
from dotenv import load_dotenv

load_dotenv()

_ENV = os.getenv("TEST_ENV", "sit").upper()


def get_db_connection(database: str = None):
    """获取数据库连接，database 为空时使用环境变量默认库"""
    return pymysql.connect(
        host=os.getenv(f"{_ENV}_DB_HOST"),
        port=int(os.getenv(f"{_ENV}_DB_PORT", 3306)),
        user=os.getenv(f"{_ENV}_DB_USER"),
        password=os.getenv(f"{_ENV}_DB_PASSWORD"),
        database=database or os.getenv(f"{_ENV}_DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def query_one(sql: str, args=None, database: str = None) -> dict:
    """执行 SQL 返回单条记录"""
    conn = get_db_connection(database)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, args)
            return cursor.fetchone()
    finally:
        conn.close()


def query_all(sql: str, args=None, database: str = None) -> list:
    """执行 SQL 返回所有记录"""
    conn = get_db_connection(database)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, args)
            return cursor.fetchall()
    finally:
        conn.close()
