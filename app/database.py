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
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """クエリを実行"""
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch_one:
                    result = cursor.fetchone()
                    if result:
                        try:
                            # PostgreSQLの場合は列名を取得してマッピング
                            if self.db_type == 'postgresql':
                                columns = [desc[0] for desc in cursor.description]
                                if len(columns) == len(result):
                                    return dict(zip(columns, result))
                                else:
                                    # フォールバック: インデックスベース
                                    return {f'col_{i}': val for i, val in enumerate(result)}
                            else:
                                return dict(result)
                        except Exception as e:
                            print(f"Result processing error: {e}")
                            # フォールバック処理
                            if hasattr(result, '__iter__') and not isinstance(result, str):
                                return {f'col_{i}': val for i, val in enumerate(result)}
                            return {'result': result}
                    return None
                elif fetch_all:
                    results = cursor.fetchall()
                    if results:
                        try:
                            # PostgreSQLの場合は列名を取得してマッピング
                            if self.db_type == 'postgresql':
                                columns = [desc[0] for desc in cursor.description]
                                if len(columns) > 0 and len(results) > 0 and len(columns) == len(results[0]):
                                    return [dict(zip(columns, row)) for row in results]
                                else:
                                    # フォールバック: インデックスベース
                                    return [{f'col_{i}': val for i, val in enumerate(row)} for row in results]
                            else:
                                return [dict(row) for row in results]
                        except Exception as e:
                            print(f"Results processing error: {e}")
                            # フォールバック処理
                            processed_results = []
                            for row in results:
                                if hasattr(row, '__iter__') and not isinstance(row, str):
                                    processed_results.append({f'col_{i}': val for i, val in enumerate(row)})
                                else:
                                    processed_results.append({'result': row})
                            return processed_results
                    return []
                else:
                    conn.commit()
                    return cursor.rowcount
            finally:
                conn.close()
        except Exception as e:
            print(f"Database query error: {e}")
            return None if fetch_one else ([] if fetch_all else 0)
            return [] if fetch_all else None
    
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