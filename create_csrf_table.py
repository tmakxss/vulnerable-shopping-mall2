import sqlite3
import os

def create_csrf_tokens_table():
    """CSRFトークン管理用のテーブルを作成"""
    db_path = os.path.join('database', 'shop.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # CSRFトークンテーブルを作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS csrf_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                is_used INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # インデックスを作成（高速検索用）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_csrf_user_token 
            ON csrf_tokens (user_id, token)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_csrf_created_at 
            ON csrf_tokens (created_at)
        ''')
        
        conn.commit()
        print("✅ CSRFトークンテーブルが正常に作成されました")
        
        # テーブル確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='csrf_tokens'")
        if cursor.fetchone():
            print("✅ csrf_tokensテーブルが存在することを確認")
        else:
            print("❌ csrf_tokensテーブルの作成に失敗")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_csrf_tokens_table()