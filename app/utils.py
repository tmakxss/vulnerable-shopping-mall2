"""
ユーティリティ関数
"""
import os
from app.database import db_manager

def get_database_status():
    """データベースの状態を確認"""
    if not db_manager:
        return False, "Database manager not initialized"
    
    try:
        # 簡単な接続テスト
        if db_manager.db_type == 'postgresql':
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
        else:
            # SQLite用のテスト
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {e}"

def safe_database_query(query, params=None, fetch_one=False, fetch_all=False, default_value=None):
    """安全なデータベースクエリ実行"""
    if not db_manager:
        return default_value
    
    try:
        return db_manager.execute_query(query, params, fetch_one, fetch_all)
    except Exception as e:
        print(f"Database query error: {e}")
        return default_value