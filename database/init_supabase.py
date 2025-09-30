import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# PostgreSQL用ドライバー（Vercel対応）
try:
    import pg8000
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

# 環境変数をロード
load_dotenv()

def init_supabase_database():
    """Supabaseデータベースの初期化"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("❌ SUPABASE_DB_URL environment variable is required")
        return False
    
    if not PG_AVAILABLE:
        print("❌ pg8000 driver is not available")
        return False
    
    try:
        # URLをパース
        parsed = urlparse(db_url)
        db_config = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # '/'を除去
            'user': parsed.username,
            'password': parsed.password
        }
        
        conn = pg8000.connect(**db_config)
        cursor = conn.cursor()
        
        print("🗄️  Supabaseデータベースの初期化を開始...")
        
        # ユーザーテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                address TEXT,
                phone VARCHAR(20),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 商品テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                stock INTEGER DEFAULT 0,
                category VARCHAR(50),
                image_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # カートテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # 注文テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                shipping_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 注文詳細テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # レビューテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # メールテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER,
                recipient_id INTEGER,
                subject VARCHAR(255),
                body TEXT,
                attachment_path VARCHAR(500),
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ データベーステーブルの作成完了")
        
        # 初期データの挿入
        insert_initial_data(cursor, conn)
        
        conn.close()
        print("🎉 Supabaseデータベースの初期化が完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ データベース初期化エラー: {e}")
        return False

def insert_initial_data(cursor, conn):
    """初期データの挿入"""
    print("📊 初期データを挿入中...")
    
    # 管理者ユーザーの作成
    cursor.execute('''
        INSERT INTO users (username, password, email, is_admin)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    ''', ('admin', 'admin123', 'admin@vulnerable-shop.com', True))
    
    # テストユーザーの作成
    cursor.execute('''
        INSERT INTO users (username, password, email, is_admin)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    ''', ('user1', 'password123', 'user1@example.com', False))
    
    cursor.execute('''
        INSERT INTO users (username, password, email, is_admin)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    ''', ('test', 'test123', 'test@example.com', False))
    
    # サンプル商品の作成
    products = [
        ('ノートパソコン', 'ハイパフォーマンスノートパソコン', 99800.00, 10, 'electronics'),
        ('スマートフォン', '最新モデルスマートフォン', 79800.00, 15, 'electronics'),
        ('Tシャツ', 'コットン100% Tシャツ', 2980.00, 50, 'clothing'),
        ('ジーンズ', 'スリムフィットジーンズ', 5980.00, 30, 'clothing'),
        ('コーヒー豆', 'プレミアムコーヒー豆', 1200.00, 100, 'food')
    ]
    
    for product in products:
        cursor.execute('''
            INSERT INTO products (name, description, price, stock, category)
            VALUES (%s, %s, %s, %s, %s)
        ''', product)
    
    conn.commit()
    print("✅ 初期データの挿入完了")

if __name__ == '__main__':
    success = init_supabase_database()
    if success:
        print("\n🚀 データベースの準備が完了しました！")
        print("🌐 Vercelへのデプロイが可能です。")
    else:
        print("\n❌ データベースの初期化に失敗しました。")
        print("🔧 環境変数の設定を確認してください。")