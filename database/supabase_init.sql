-- 脆弱なショッピングモール データベース初期化スクリプト
-- Supabase SQLエディタで実行してください

-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品テーブル
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    category VARCHAR(50),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- カートテーブル
CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- 注文テーブル
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 注文詳細テーブル
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- レビューテーブル
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- メールテーブル
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
);

-- 初期データ挿入

-- 管理者ユーザー
INSERT INTO users (username, password, email, is_admin)
VALUES ('admin', 'admin123', 'admin@vulnerable-shop.com', TRUE)
ON CONFLICT (username) DO NOTHING;

-- テストユーザー
INSERT INTO users (username, password, email, is_admin)
VALUES ('user1', 'password123', 'user1@example.com', FALSE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, password, email, is_admin)
VALUES ('test', 'test123', 'test@example.com', FALSE)
ON CONFLICT (username) DO NOTHING;

-- サンプル商品
INSERT INTO products (name, description, price, stock, category) VALUES
('ノートパソコン', 'ハイパフォーマンスノートパソコン', 99800.00, 10, 'electronics'),
('スマートフォン', '最新モデルスマートフォン', 79800.00, 15, 'electronics'),
('Tシャツ', 'コットン100% Tシャツ', 2980.00, 50, 'clothing'),
('ジーンズ', 'スリムフィットジーンズ', 5980.00, 30, 'clothing'),
('コーヒー豆', 'プレミアムコーヒー豆', 1200.00, 100, 'food'),
('無線イヤホン', 'ノイズキャンセリング機能付き', 15800.00, 25, 'electronics'),
('パーカー', '裏起毛フーディー', 4980.00, 40, 'clothing'),
('グリーンティー', 'オーガニック緑茶', 800.00, 80, 'food');

-- サンプルレビュー
INSERT INTO reviews (product_id, user_id, rating, comment) VALUES
(1, 2, 5, '素晴らしい商品です！<script>alert("XSS")</script>'),
(2, 3, 4, '良い商品でした。配送も早かったです。'),
(3, 2, 3, '普通のTシャツです。'),
(1, 3, 5, '期待以上の性能でした！おすすめします。');

-- データベース初期化完了メッセージ
SELECT 'データベース初期化が完了しました！' as message;