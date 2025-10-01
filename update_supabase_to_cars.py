import os
import psycopg2
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

def update_supabase_products_to_cars():
    """Supabaseの既存商品データを車に置き換え"""
    
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
        
        # 現在の商品数を確認
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"📊 現在の商品数: {product_count}")
        
        # 車の商品データ（19種類）
        car_products = [
            {
                'id': 1,
                'name': 'トヨタ プリウス',
                'description': '環境に優しいハイブリッド車。燃費性能抜群で経済的。都市部の運転に最適な一台です。',
                'price': 2800000.00,
                'stock': 5,
                'category': '乗用車',
                'image_url': '/static/cars/Gemini_Generated_Image_3wme343wme343wme.png'
            },
            {
                'id': 2,
                'name': 'ホンダ フィット',
                'description': 'コンパクトで取り回しの良い人気車種。初心者にもおすすめの扱いやすい車です。',
                'price': 1900000.00,
                'stock': 8,
                'category': 'コンパクトカー',
                'image_url': '/static/cars/Gemini_Generated_Image_3wme343wme343wme (1).png'
            },
            {
                'id': 3,
                'name': 'BMW 3シリーズ',
                'description': 'ドイツの高級セダン。優れた走行性能と上質な内装が魅力の一台。',
                'price': 5200000.00,
                'stock': 3,
                'category': '高級車',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz.png'
            },
            {
                'id': 4,
                'name': 'メルセデス・ベンツ Cクラス',
                'description': '洗練されたデザインと快適性を兼ね備えた高級セダン。ステータスシンボルとしても人気。',
                'price': 6800000.00,
                'stock': 2,
                'category': '高級車',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (1).png'
            },
            {
                'id': 5,
                'name': 'アウディ A4',
                'description': 'スポーティーな走りと実用性を両立したプレミアムセダン。先進技術が満載。',
                'price': 4900000.00,
                'stock': 4,
                'category': '高級車',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (2).png'
            },
            {
                'id': 6,
                'name': '日産 セレナ',
                'description': 'ファミリーに最適な7人乗りミニバン。広い室内空間と便利な機能が充実。',
                'price': 3200000.00,
                'stock': 6,
                'category': 'ミニバン',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (3).png'
            },
            {
                'id': 7,
                'name': 'マツダ CX-5',
                'description': 'スタイリッシュなSUV。アウトドアにも街乗りにも対応する万能車。',
                'price': 3600000.00,
                'stock': 7,
                'category': 'SUV',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (4).png'
            },
            {
                'id': 8,
                'name': 'スバル フォレスター',
                'description': '悪路走破性に優れたSUV。安全性能も高く、アクティブな方におすすめ。',
                'price': 3300000.00,
                'stock': 5,
                'category': 'SUV',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (5).png'
            },
            {
                'id': 9,
                'name': 'レクサス IS',
                'description': '日本の高級スポーツセダン。洗練されたデザインと卓越した品質。',
                'price': 5800000.00,
                'stock': 3,
                'category': '高級車',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (6).png'
            },
            {
                'id': 10,
                'name': 'トヨタ ヴォクシー',
                'description': 'スタイリッシュなミニバン。家族でのお出かけに最適な広々とした空間。',
                'price': 3400000.00,
                'stock': 6,
                'category': 'ミニバン',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (7).png'
            },
            {
                'id': 11,
                'name': 'ホンダ ヴェゼル',
                'description': 'クーペライクなスタイリングのコンパクトSUV。都市部での使用に最適。',
                'price': 2700000.00,
                'stock': 8,
                'category': 'SUV',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (8).png'
            },
            {
                'id': 12,
                'name': 'ダイハツ タント',
                'description': '軽自動車とは思えない広い室内。燃費も良く経済的な一台。',
                'price': 1600000.00,
                'stock': 12,
                'category': '軽自動車',
                'image_url': '/static/cars/Gemini_Generated_Image_i8rz02i8rz02i8rz (9).png'
            },
            {
                'id': 13,
                'name': 'スズキ ハスラー',
                'description': 'アウトドアテイストの軽SUV。個性的なデザインで人気の車種。',
                'price': 1800000.00,
                'stock': 10,
                'category': '軽自動車',
                'image_url': '/static/cars/Gemini_Generated_Image_mh4zy9mh4zy9mh4z.png'
            },
            {
                'id': 14,
                'name': 'トヨタ ランドクルーザー',
                'description': '本格的なオフロード性能を持つ大型SUV。どんな道でも走破する頼もしい相棒。',
                'price': 7200000.00,
                'stock': 2,
                'category': 'SUV',
                'image_url': '/static/cars/Gemini_Generated_Image_mh4zy9mh4zy9mh4z (1).png'
            },
            {
                'id': 15,
                'name': 'ポルシェ 911',
                'description': 'スポーツカーの代名詞。圧倒的な加速性能とハンドリングが魅力。',
                'price': 12000000.00,
                'stock': 1,
                'category': 'スポーツカー',
                'image_url': '/static/cars/Gemini_Generated_Image_mh4zy9mh4zy9mh4z (2).png'
            },
            {
                'id': 16,
                'name': 'フェラーリ 488',
                'description': 'イタリアンスーパーカー。美しいデザインと圧巻のパフォーマンス。',
                'price': 30000000.00,
                'stock': 1,
                'category': 'スポーツカー',
                'image_url': '/static/cars/Gemini_Generated_Image_pnf89cpnf89cpnf8.png'
            },
            {
                'id': 17,
                'name': 'ランボルギーニ ウラカン',
                'description': '究極のスーパーカー。アグレッシブなデザインと圧倒的な性能。',
                'price': 28000000.00,
                'stock': 1,
                'category': 'スポーツカー',
                'image_url': '/static/cars/Gemini_Generated_Image_pnf89cpnf89cpnf8 (1).png'
            },
            {
                'id': 18,
                'name': 'テスラ Model 3',
                'description': '先進的な電気自動車。環境性能と最新技術が融合した未来の車。',
                'price': 5500000.00,
                'stock': 3,
                'category': '電気自動車',
                'image_url': '/static/cars/Gemini_Generated_Image_pnf89cpnf89cpnf8 (2).png'
            },
            {
                'id': 19,
                'name': 'トヨタ アルファード',
                'description': '最高級ミニバン。VIP仕様の豪華な内装と快適な乗り心地。',
                'price': 4800000.00,
                'stock': 4,
                'category': 'ミニバン',
                'image_url': '/static/cars/Gemini_Generated_Image_tj6eb4tj6eb4tj6e (1).png'
            }
        ]
        
        print("🚗 既存商品データを車に置き換え中...")
        
        # 各商品データを更新
        for car in car_products:
            cursor.execute('''
                UPDATE products 
                SET name = %s, description = %s, price = %s, stock = %s, category = %s, image_url = %s
                WHERE id = %s
            ''', (car['name'], car['description'], car['price'], car['stock'], car['category'], car['image_url'], car['id']))
            
            print(f"✅ ID {car['id']}: {car['name']} - ¥{car['price']:,}")
        
        # 変更をコミット
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Supabaseの商品データ更新が完了しました！")
        print(f"19種類の車商品に置き換えました。")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    update_supabase_products_to_cars()