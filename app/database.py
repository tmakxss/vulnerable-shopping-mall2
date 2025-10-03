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
        self.connection_error = None
        
        if self.db_type == 'postgresql':
            self.db_url = os.getenv('SUPABASE_DB_URL')
            if not self.db_url:
                self.connection_error = "SUPABASE_DB_URL environment variable is required for PostgreSQL"
                return
            
            # URLをパース
            try:
                parsed = urlparse(self.db_url)
                self.db_config = {
                    'host': parsed.hostname,
                    'port': parsed.port or 5432,
                    'database': parsed.path[1:],  # '/'を除去
                    'user': parsed.username,
                    'password': parsed.password
                }
            except Exception as e:
                self.connection_error = f"Database URL parsing error: {e}"
        else:
            self.db_path = os.getenv('SQLITE_DB_PATH', 'database/shop.db')
    
    def get_connection(self):
        """データベース接続を取得"""
        if self.connection_error:
            raise Exception(f"Database connection error: {self.connection_error}")
            
        if self.db_type == 'postgresql' and PG_AVAILABLE:
            try:
                return pg8000.connect(**self.db_config)
            except Exception as e:
                raise Exception(f"PostgreSQL connection failed: {e}")
        else:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                return conn
            except Exception as e:
                raise Exception(f"SQLite connection failed: {e}")
    
    def _convert_value(self, value):
        """PostgreSQLの特殊な型を標準の型に変換"""
        from decimal import Decimal
        import datetime
        
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        return value
    
    def _process_row(self, row, columns):
        """行データを辞書に変換"""
        try:
            if self.db_type == 'postgresql':
                # PostgreSQLの場合：リストとして返される
                converted_row = [self._convert_value(val) for val in row]
                return dict(zip(columns, converted_row))
            else:
                # SQLiteの場合：Row オブジェクト
                return dict(row)
        except Exception as e:
            print(f"Row processing error: {e}")
            # フォールバック処理
            return {f'col_{i}': self._convert_value(val) for i, val in enumerate(row)}

    def _convert_query_params(self, query, params):
        """データベースタイプに応じてクエリパラメータを変換"""
        if self.db_type == 'postgresql' and params:
            # PostgreSQL用: ? を %s に変換
            converted_query = query.replace('?', '%s')
            return converted_query, params
        return query, params

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """クエリを実行"""
        conn = None
        try:
            # クエリとパラメータを変換
            converted_query, converted_params = self._convert_query_params(query, params)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            print(f"Executing query: {converted_query}")  # デバッグ用
            print(f"With params: {converted_params}")  # デバッグ用
            
            if converted_params:
                cursor.execute(converted_query, converted_params)
            else:
                cursor.execute(converted_query)
            
            if fetch_one:
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    return self._process_row(result, columns)
                return None
            elif fetch_all:
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]
                    return [self._process_row(row, columns) for row in results]
                return []
            else:
                # INSERT/UPDATE/DELETE操作の場合
                conn.commit()
                affected_rows = cursor.rowcount
                print(f"Committed to database, affected rows: {affected_rows}")  # デバッグ用
                return affected_rows
                
        except Exception as e:
            print(f"Database query error: {e}")
            if conn:
                try:
                    conn.rollback()
                    print("Transaction rolled back")
                except:
                    pass
            return None if fetch_one else ([] if fetch_all else 0)
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
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
try:
    db_manager = DatabaseManager()
except Exception as e:
    print(f"Database manager initialization error: {e}")
    db_manager = None