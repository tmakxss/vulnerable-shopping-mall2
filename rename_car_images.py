#!/usr/bin/env python3
import os
import shutil
import psycopg2
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def rename_image_files():
    """画像ファイル名をURL-safeに変更し、データベースも更新"""
    
    cars_dir = "app/static/cars"
    
    # ファイル名変更マッピング
    file_renames = {
        "alpine a110.png": "alpine-a110.png",
        "alpine a110R.png": "alpine-a110r.png",
        "benz amg 45.png": "mercedes-amg-a45s.png",
        "bmw m4.png": "bmw-m4.png",
        "honda civc type R.png": "honda-civic-type-r.png",
        "honda nsx.png": "honda-nsx.png",
        "nissan 180sx.png": "nissan-180sx.png",
        "nissan gtr r33.png": "nissan-gtr-r33.png",
        "nissan r34.png": "nissan-skyline-r34.png",
        "nissan s15シルビア.png": "nissan-silvia-s15.png",
        "porshe 718.png": "porsche-718-cayman.png",
        "porshe 911 (2).png": "porsche-911-turbo-s.png",
        "subaru wrx sti.png": "subaru-wrx-sti.png",
        "toyota AE86.png": "toyota-ae86.png",
        "toyota gr86.png": "toyota-gr86.png"
    }
    
    # データベース更新マッピング
    db_updates = [
        (1, '/static/cars/alpine-a110.png'),
        (2, '/static/cars/alpine-a110r.png'),
        (3, '/static/cars/mercedes-amg-a45s.png'),
        (4, '/static/cars/bmw-m4.png'),
        (5, '/static/cars/honda-civic-type-r.png'),
        (6, '/static/cars/honda-nsx.png'),
        (7, '/static/cars/nissan-180sx.png'),
        (8, '/static/cars/nissan-gtr-r33.png'),
        (9, '/static/cars/nissan-skyline-r34.png'),
        (10, '/static/cars/nissan-silvia-s15.png'),
        (11, '/static/cars/porsche-718-cayman.png'),
        (12, '/static/cars/porsche-911-turbo-s.png'),
        (13, '/static/cars/subaru-wrx-sti.png'),
        (14, '/static/cars/toyota-ae86.png'),
        (15, '/static/cars/toyota-gr86.png'),
        (16, '/static/cars/toyota-gr86.png'),  # Supraも同じ画像
    ]
    
    print("🔄 画像ファイル名をURL-safe形式に変更中...")
    
    # ファイル名変更
    for old_name, new_name in file_renames.items():
        old_path = os.path.join(cars_dir, old_name)
        new_path = os.path.join(cars_dir, new_name)
        
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"✅ {old_name} → {new_name}")
        else:
            print(f"⚠️  {old_name} が見つかりません")
    
    # データベース更新
    try:
        conn = psycopg2.connect(os.getenv('SUPABASE_DB_URL'))
        cursor = conn.cursor()
        
        print("\n🔄 データベースの画像パスを更新中...")
        
        for product_id, image_path in db_updates:
            cursor.execute(
                "UPDATE products SET image_url = %s WHERE id = %s",
                (image_path, product_id)
            )
            print(f"✅ 商品ID {product_id}: {image_path}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ {len(db_updates)}個の商品の画像パスを更新しました")
        
    except Exception as e:
        print(f"❌ データベース更新エラー: {e}")
    
    print("\n📁 変更後のファイル一覧:")
    if os.path.exists(cars_dir):
        files = os.listdir(cars_dir)
        for file in sorted(files):
            print(f"  - {file}")

if __name__ == "__main__":
    rename_image_files()