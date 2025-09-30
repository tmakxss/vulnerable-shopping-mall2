import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import sqlite3

class DatabaseManager:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite')
        
        if self.db_type == 'postgresql':
            self.db_url = os.getenv('SUPABASE_DB_URL')
            if not self.db_url:
                raise ValueError("SUPABASE_DB_URL environment variable is required for PostgreSQL")
        else:
            self.db_path = os.getenv('SQLITE_DB_PATH', 'database/shop.db')
    
    def get_connection(self):
        """データベース接続を取得"""
        if self.db_type == 'postgresql':
            return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
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