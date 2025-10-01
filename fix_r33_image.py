#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def fix_r33_image():
    """R33の画像パスを修正"""
    try:
        # Supabaseに接続
        conn = psycopg2.connect(os.getenv('SUPABASE_DB_URL'))
        cursor = conn.cursor()
        
        print("🔄 R33の画像パスを修正中...")
        
        # 商品ID 16 (Nissan Skyline GT-R R33) の画像パスを修正
        cursor.execute(
            "UPDATE products SET image_url = %s WHERE id = %s",
            ('/static/cars/nissan-gtr-r33.png', 16)
        )
        
        conn.commit()
        print("✅ R33の画像パスを修正しました")
        
        # 修正後の確認
        cursor.execute("SELECT id, name, image_url FROM products WHERE id = 16")
        product = cursor.fetchone()
        
        if product:
            print(f"\n修正後: ID: {product[0]}, 名前: {product[1]}, 画像: {product[2]}")
        
        # 全商品の画像パス確認
        cursor.execute("SELECT id, name, image_url FROM products ORDER BY id")
        products = cursor.fetchall()
        
        print("\n全商品の画像パス:")
        for product in products:
            print(f"ID: {product[0]:2d}, 名前: {product[1]:<25s}, 画像: {product[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_r33_image()