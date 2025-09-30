import os
import sqlite3
from urllib.parse import urlparse

# PostgreSQL用ドライバー（Vercel対応）
try:
    import pg8000
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

class DatabaseManager:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite')
        
        if self.db_type == 'postgresql':
            self.db_url = os.getenv('SUPABASE_DB_URL')
            if not self.db_url:
                raise ValueError("SUPABASE_DB_URL environment variable is required for PostgreSQL")
            
            # URLをパース
            parsed = urlparse(self.db_url)
            self.db_config = {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'database': parsed.path[1:],  # '/'を除去
                'user': parsed.username,
                'password': parsed.password
            }
        else:
            self.db_path = os.getenv('SQLITE_DB_PATH', 'database/shop.db')
    
    def get_connection(self):
        """データベース接続を取得"""
        if self.db_type == 'postgresql' and PG_AVAILABLE:
            return pg8000.connect(**self.db_config)
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """クエリを実行"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()
    
    def execute_script(self, script):
        """スクリプトを実行（初期化用）"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(script)
            conn.commit()
        finally:
            conn.close()

# グローバルインスタンス
db_manager = DatabaseManager()