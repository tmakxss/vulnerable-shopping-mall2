import os
import psycopg2
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

def update_categories_by_brand():
    """商品カテゴリをブランド名に統一"""
    
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
        
        # ブランド別カテゴリ更新データ
        brand_updates = [
            {
                'id': 1,
                'category': 'Alpine'
            },
            {
                'id': 2,
                'category': 'Alpine'
            },
            {
                'id': 3,
                'category': 'Mercedes-Benz'
            },
            {
                'id': 4,
                'category': 'BMW'
            },
            {
                'id': 5,
                'category': 'Honda'
            },
            {
                'id': 6,
                'category': 'Honda'
            },
            {
                'id': 7,
                'category': 'Nissan'
            },
            {
                'id': 8,
                'category': 'Nissan'
            },
            {
                'id': 9,
                'category': 'Nissan'
            },
            {
                'id': 10,
                'category': 'Nissan'
            },
            {
                'id': 11,
                'category': 'Porsche'
            },
            {
                'id': 12,
                'category': 'Porsche'
            },
            {
                'id': 13,
                'category': 'Subaru'
            },
            {
                'id': 14,
                'category': 'Toyota'
            },
            {
                'id': 15,
                'category': 'Toyota'
            },
            {
                'id': 16,
                'category': 'Nissan'
            }
        ]
        
        print("🏷️  カテゴリをブランド名に更新中...")
        
        # 各商品のカテゴリを更新
        for item in brand_updates:
            cursor.execute('''
                UPDATE products 
                SET category = %s
                WHERE id = %s
            ''', (item['category'], item['id']))
            
            # 商品名も取得して表示
            cursor.execute('SELECT name FROM products WHERE id = %s', (item['id'],))
            product_name = cursor.fetchone()[0]
            
            print(f"✅ ID {item['id']}: {product_name} → カテゴリ: {item['category']}")
        
        # 変更をコミット
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 カテゴリをブランド名に統一しました！")
        print("商品がブランド別に整理されました。")
        
        # ブランド別商品数を表示
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category 
            ORDER BY category
        ''')
        brand_counts = cursor.fetchall()
        
        print("\n📊 ブランド別商品数:")
        for brand, count in brand_counts:
            print(f"   {brand}: {count}台")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    update_categories_by_brand()