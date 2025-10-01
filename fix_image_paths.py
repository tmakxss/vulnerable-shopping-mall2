#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def fix_image_paths():
    """商品の画像パスを修正"""
    try:
        # Supabaseに接続
        conn = psycopg2.connect(os.getenv('SUPABASE_DB_URL'))
        cursor = conn.cursor()
        
        # 画像パスの修正マッピング
        image_fixes = [
            (1, '/static/cars/alpine a110.png'),           # Alpine A110
            (2, '/static/cars/alpine a110R.png'),          # Alpine A110R
            (3, '/static/cars/benz amg 45.png'),           # Mercedes-AMG A45 S
            (4, '/static/cars/bmw m4.png'),                # BMW M4
            (5, '/static/cars/honda civc type R.png'),     # Honda Civic Type R
            (6, '/static/cars/honda nsx.png'),             # Honda NSX
            (7, '/static/cars/nissan 180sx.png'),          # Nissan 180SX
            (8, '/static/cars/nissan gtr r33.png'),        # Nissan GT-R R35 (実際はR33画像)
            (9, '/static/cars/nissan r34.png'),            # Nissan Skyline GT-R R34
            (10, '/static/cars/nissan s15シルビア.png'),    # Nissan Silvia S15
            (11, '/static/cars/porshe 718.png'),           # Porsche 718 Cayman
            (12, '/static/cars/porshe 911 (2).png'),       # Porsche 911 Turbo S
            (13, '/static/cars/subaru wrx sti.png'),       # Subaru WRX STI
            (14, '/static/cars/toyota AE86.png'),          # Toyota AE86
            (15, '/static/cars/toyota gr86.png'),          # Toyota GR86
            (16, '/static/cars/toyota gr86.png'),          # Toyota Supra (GR86画像を使用)
        ]
        
        print("画像パスを修正中...")
        
        for product_id, image_path in image_fixes:
            cursor.execute(
                "UPDATE products SET image_url = %s WHERE id = %s",
                (image_path, product_id)
            )
            print(f"商品ID {product_id}: {image_path}")
        
        conn.commit()
        print(f"\n✅ {len(image_fixes)}個の商品の画像パスを修正しました")
        
        # 修正後の確認
        cursor.execute("SELECT id, name, image_url FROM products ORDER BY id")
        products = cursor.fetchall()
        
        print("\n修正後の画像パス:")
        for product in products:
            print(f"ID: {product[0]}, 名前: {product[1]}, 画像: {product[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_image_paths()