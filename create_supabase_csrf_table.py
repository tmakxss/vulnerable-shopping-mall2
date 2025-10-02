import os
from app.database import db_manager

def create_csrf_tokens_table():
    """SupabaseにCSRFトークン管理用のテーブルを作成"""
    
    if not db_manager:
        print("❌ Database manager not initialized")
        return False
        
    if db_manager.db_type != 'postgresql':
        print("❌ This script is for PostgreSQL/Supabase only")
        return False
        
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        print("🔄 Supabaseデータベースに接続中...")
        
        # CSRFトークンテーブルを作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS csrf_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at BIGINT NOT NULL,
                is_used INTEGER DEFAULT 0,
                CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        ''')
        
        # インデックスを作成（高速検索用）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_csrf_user_token 
            ON csrf_tokens (user_id, token);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_csrf_created_at 
            ON csrf_tokens (created_at);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_csrf_is_used 
            ON csrf_tokens (is_used);
        ''')
        
        conn.commit()
        print("✅ CSRFトークンテーブルがSupabaseに正常に作成されました")
        
        # テーブル確認
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'csrf_tokens'
        """)
        
        if cursor.fetchone():
            print("✅ csrf_tokensテーブルがSupabaseに存在することを確認")
            
            # カラム情報を表示
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'csrf_tokens' 
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("📋 テーブル構造:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                
        else:
            print("❌ csrf_tokensテーブルの作成に失敗")
            return False
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Supabaseエラー: {e}")
        return False

def test_csrf_token_operations():
    """CSRFトークン操作のテスト"""
    if not db_manager or db_manager.db_type != 'postgresql':
        print("❌ PostgreSQL/Supabase環境が必要です")
        return
        
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        print("🧪 CSRFトークン操作のテスト開始...")
        
        # テストデータの挿入
        test_token = "test_token_12345"
        test_user_id = 1
        import time
        timestamp = int(time.time())
        
        cursor.execute("""
            INSERT INTO csrf_tokens (user_id, token, created_at, is_used) 
            VALUES (%s, %s, %s, 0)
            ON CONFLICT (token) DO NOTHING
        """, (test_user_id, test_token, timestamp))
        
        # トークン検索テスト
        cursor.execute("""
            SELECT token, is_used FROM csrf_tokens 
            WHERE user_id = %s AND token = %s
        """, (test_user_id, test_token))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ トークン検索成功: {result[0][:8]}..., is_used: {result[1]}")
        
        # 使用済みマーク テスト
        cursor.execute("""
            UPDATE csrf_tokens 
            SET is_used = 1 
            WHERE user_id = %s AND token = %s AND is_used = 0
        """, (test_user_id, test_token))
        
        affected = cursor.rowcount
        print(f"✅ 使用済みマーク: {affected}行更新")
        
        # 再度使用済みマーク（失敗するはず）
        cursor.execute("""
            UPDATE csrf_tokens 
            SET is_used = 1 
            WHERE user_id = %s AND token = %s AND is_used = 0
        """, (test_user_id, test_token))
        
        affected = cursor.rowcount
        print(f"✅ 再利用防止テスト: {affected}行更新（0であるべき）")
        
        # テストデータ削除
        cursor.execute("DELETE FROM csrf_tokens WHERE token = %s", (test_token,))
        
        conn.commit()
        conn.close()
        print("✅ CSRFトークン操作テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")

if __name__ == "__main__":
    print("🚀 Supabase CSRFトークンテーブル作成開始...")
    
    if create_csrf_tokens_table():
        print("\n🧪 動作テストを実行中...")
        test_csrf_token_operations()
        print("\n🎉 セットアップ完了！")
    else:
        print("\n❌ セットアップ失敗")