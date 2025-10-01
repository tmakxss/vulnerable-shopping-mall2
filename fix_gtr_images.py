#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def fix_gtr_images():
    """GT-R R35とR33の画像を正しく割り当て"""
    try:
        # Supabaseに接続
        conn = psycopg2.connect(os.getenv('SUPABASE_DB_URL'))
        cursor = conn.cursor()
        
        print("🔄 GT-R画像を修正中...")
        
        # 現在利用可能な画像を確認
        available_images = [
            '/static/cars/nissan-gtr-r33.png',      # R33用
            '/static/cars/nissan-skyline-r34.png',  # R34用  
            '/static/cars/nissan-180sx.png',        # 180SX用
            '/static/cars/nissan-silvia-s15.png',   # S15用
        ]
        
        print("利用可能なNissan画像:")
        for img in available_images:
            print(f"  - {img}")
        
        # GT-R R35（ID: 8）には一時的にR33の画像を使用（名前だけ異なる）
        # GT-R R33（ID: 16）にはR33の画像を使用
        
        # 実際にはR35とR33は同じ画像ファイルを共有（画像が同じため）
        updates = [
            (8, '/static/cars/nissan-gtr-r33.png', 'Nissan GT-R R35'),   # R35だがR33画像使用
            (16, '/static/cars/nissan-gtr-r33.png', 'Nissan Skyline GT-R R33')  # R33画像
        ]
        
        for product_id, image_path, name in updates:
            cursor.execute(
                "UPDATE products SET image_url = %s WHERE id = %s",
                (image_path, product_id)
            )
            print(f"✅ 商品ID {product_id} ({name}): {image_path}")
        
        conn.commit()
        print("\n✅ GT-R画像パスを修正しました")
        
        # 修正後の確認
        cursor.execute("""
            SELECT id, name, image_url 
            FROM products 
            WHERE name LIKE '%GT-R%' OR name LIKE '%Skyline%'
            ORDER BY id
        """)
        products = cursor.fetchall()
        
        print("\nGT-R関連商品:")
        for product in products:
            print(f"ID: {product[0]:2d}, 名前: {product[1]:<25s}, 画像: {product[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_gtr_images()