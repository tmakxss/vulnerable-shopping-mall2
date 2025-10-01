import os
import psycopg2
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

def update_supabase_products_to_cars_safe():
    """Supabaseの商品データを安全に車データに更新"""
    
    # .envからSupabaseの接続情報を取得
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
    
    if not SUPABASE_DB_URL:
        print("❌ SUPABASE_DB_URLが見つかりません")
        return
    
    try:
        # PostgreSQL接続
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cursor = conn.cursor()
        
        print("🔗 Supabaseに接続しました")
        
        # 既存のテーブル構造を確認
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"📋 既存テーブル: {[t[0] for t in tables]}")
        
        # reviewsテーブルのみクリア（存在する場合）
        try:
            cursor.execute("DELETE FROM reviews")
            print("🗑️  reviewsテーブルをクリアしました")
        except:
            print("ℹ️  reviewsテーブルが存在しないか、すでに空です")
        
        # 画像ファイル名に基づいた正確な車データ（16台）
        car_products = [
            {
                'id': 1,
                'name': 'Alpine A110',
                'description': 'フランスの軽量スポーツカー。アルミニウムスペースフレームとカーボンファイバーボディで極限まで軽量化。1.8L直4ターボエンジンで卓越したハンドリングを実現。',
                'price': 8500000.00,
                'stock': 2,
                'category': 'スポーツカー',
                'image_url': '/static/cars/alpine a110.png'
            },
            {
                'id': 2,
                'name': 'Alpine A110R',
                'description': 'A110の究極バージョン。サーキット走行を重視したハードコア仕様。エアロパッケージとロールケージを装備し、さらなる軽量化を実現。',
                'price': 12000000.00,
                'stock': 1,
                'category': 'スポーツカー',
                'image_url': '/static/cars/alpine a110R.png'
            },
            {
                'id': 3,
                'name': 'Mercedes-AMG A45 S',
                'description': '世界最強の2.0L 4気筒ターボエンジンを搭載するホットハッチ。421PSの圧倒的パワーと4WDシステムで驚異的な加速性能を発揮。',
                'price': 9200000.00,
                'stock': 3,
                'category': '高性能車',
                'image_url': '/static/cars/benz amg 45.png'
            },
            {
                'id': 4,
                'name': 'BMW M4',
                'description': '3.0L直6ツインターボエンジンを搭載するハイパフォーマンスクーペ。510PSの強力なパワーとBMW伝統の駆け抜ける歓びを体現。',
                'price': 14500000.00,
                'stock': 2,
                'category': '高性能車',
                'image_url': '/static/cars/bmw m4.png'
            },
            {
                'id': 5,
                'name': 'Honda Civic Type R',
                'description': 'ホンダのフラッグシップFF車。2.0L VTECターボエンジンで330PSを発生。ニュルブルクリンクFF最速記録を樹立した本格スポーツカー。',
                'price': 4950000.00,
                'stock': 5,
                'category': 'スポーツカー',
                'image_url': '/static/cars/honda civc type R.png'
            },
            {
                'id': 6,
                'name': 'Honda NSX',
                'description': '日本のスーパーカー。3.5L V6ツインターボエンジンと3つのモーターによるハイブリッドシステム。総出力581PSの圧倒的パフォーマンス。',
                'price': 24200000.00,
                'stock': 1,
                'category': 'スーパーカー',
                'image_url': '/static/cars/honda nsx.png'
            },
            {
                'id': 7,
                'name': 'Nissan 180SX',
                'description': '90年代を代表するスポーツカー。CA18DETエンジン搭載のピュアスポーツ。軽量ボディと後輪駆動でドリフトシーンでも人気の名車。',
                'price': 3500000.00,
                'stock': 4,
                'category': 'クラシックスポーツ',
                'image_url': '/static/cars/nissan 180sx.png'
            },
            {
                'id': 8,
                'name': 'Nissan GT-R R33',
                'description': 'スカイラインGT-Rの第3世代。RB26DETTエンジンと4WDシステムATTESAを搭載。「技術の日産」を象徴する伝説的スポーツカー。',
                'price': 8000000.00,
                'stock': 2,
                'category': 'クラシックスポーツ',
                'image_url': '/static/cars/nissan gtr r33.png'
            },
            {
                'id': 9,
                'name': 'Nissan Skyline GT-R R34',
                'description': 'スカイラインGT-Rの最終進化形。映画「ワイルドスピード」でも有名。RB26DETTエンジンの完成形として多くのファンに愛される名車。',
                'price': 15000000.00,
                'stock': 1,
                'category': 'クラシックスポーツ',
                'image_url': '/static/cars/nissan r34.png'
            },
            {
                'id': 10,
                'name': 'Nissan Silvia S15',
                'description': 'シルビア最終型。SR20DETエンジン搭載の後輪駆動スポーツカー。美しいクーペボディと優れたバランスでドリフト愛好家に絶大な人気。',
                'price': 4200000.00,
                'stock': 3,
                'category': 'クラシックスポーツ',
                'image_url': '/static/cars/nissan s15シルビア.png'
            },
            {
                'id': 11,
                'name': 'Porsche 718 Cayman',
                'description': 'ポルシェのミッドシップスポーツカー。2.0L/2.5L水平対向4気筒ターボエンジン。完璧な重量配分と卓越したハンドリングが魅力。',
                'price': 7800000.00,
                'stock': 4,
                'category': 'スポーツカー',
                'image_url': '/static/cars/porshe 718.png'
            },
            {
                'id': 12,
                'name': 'Porsche 911',
                'description': 'スポーツカーの頂点。水平対向6気筒エンジンをリアに搭載するユニークなレイアウト。60年以上の歴史を持つ永遠のベンチマーク。',
                'price': 13500000.00,
                'stock': 2,
                'category': 'スポーツカー',
                'image_url': '/static/cars/porshe 911 (2).png'
            },
            {
                'id': 13,
                'name': 'Subaru WRX STI',
                'description': '水平対向4気筒ターボエンジンとシンメトリカルAWDを搭載。WRCで培った技術を市販車に投入した本格的なスポーツセダン。',
                'price': 4100000.00,
                'stock': 6,
                'category': 'スポーツセダン',
                'image_url': '/static/cars/subaru wrx sti.png'
            },
            {
                'id': 14,
                'name': 'Toyota AE86',
                'description': '伝説のハチロク。4A-GEエンジンと後輪駆動の軽量ボディ。頭文字Dで一躍有名になった峠の名車。完璧なFRレイアウトでドライビングの基本を学べる。',
                'price': 2800000.00,
                'stock': 5,
                'category': 'クラシックスポーツ',
                'image_url': '/static/cars/toyota AE86.png'
            },
            {
                'id': 15,
                'name': 'Toyota GR86',
                'description': 'ハチロクの現代版。スバルと共同開発した2.4L水平対向4気筒エンジン。純粋な後輪駆動の楽しさを現代に蘇らせたピュアスポーツカー。',
                'price': 3100000.00,
                'stock': 7,
                'category': 'スポーツカー',
                'image_url': '/static/cars/toyota gr86.png'
            },
            {
                'id': 16,
                'name': 'Nissan Fairlady Z',
                'description': '日本を代表するスポーツカー。3.0L V6ツインターボエンジンで400PSを発生。50年以上の歴史を持つZの最新進化形。',
                'price': 5200000.00,
                'stock': 4,
                'category': 'スポーツカー',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz.png'
            }
        ]
        
        print("🚗 商品データを正確な車データに更新中...")
        
        # 各商品を個別に更新または挿入
        for car in car_products:
            # 既存商品があるかチェック
            cursor.execute("SELECT id FROM products WHERE id = %s", (car['id'],))
            exists = cursor.fetchone()
            
            if exists:
                # 更新
                cursor.execute('''
                    UPDATE products 
                    SET name = %s, description = %s, price = %s, stock = %s, category = %s, image_url = %s
                    WHERE id = %s
                ''', (car['name'], car['description'], car['price'], car['stock'], car['category'], car['image_url'], car['id']))
            else:
                # 挿入
                cursor.execute('''
                    INSERT INTO products (id, name, description, price, stock, category, image_url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ''', (car['id'], car['name'], car['description'], car['price'], car['stock'], car['category'], car['image_url']))
            
            print(f"✅ ID {car['id']}: {car['name']} - ¥{car['price']:,}")
        
        # 変更をコミット
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Supabaseに16台の正確な車データを更新しました！")
        print("画像ファイル名に基づいた正確なブランド・車種名・相場価格で完了。")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    update_supabase_products_to_cars_safe()