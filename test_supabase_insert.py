#!/usr/bin/env python3
"""
Supabaseの商品追加テスト
"""
import os
import sys
from app.database import db_manager

def test_supabase_insert():
    """Supabaseへの商品追加テスト"""
    print("=== Supabase商品追加テスト ===")
    
    # データベース設定確認
    print(f"データベースタイプ: {db_manager.db_type}")
    print(f"Supabase URL設定: {'あり' if os.getenv('SUPABASE_DB_URL') else 'なし'}")
    
    try:
        # 接続テスト
        conn = db_manager.get_connection()
        print("✓ Supabase接続成功")
        conn.close()
        
        # 現在の商品数確認
        current_count = db_manager.execute_query(
            "SELECT COUNT(*) FROM products",
            fetch_one=True
        )
        print(f"現在の商品数: {current_count}")
        
        # テスト商品追加
        test_product = {
            'name': 'テスト商品_' + str(int(__import__('time').time())),
            'description': 'Supabaseテスト用商品',
            'price': 1000,
            'stock': 10,
            'category': 'テスト',
            'image_url': '/static/test.jpg'
        }
        
        print(f"追加する商品: {test_product}")
        
        result = db_manager.execute_query(
            "INSERT INTO products (name, description, price, stock, category, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (test_product['name'], test_product['description'], test_product['price'], 
             test_product['stock'], test_product['category'], test_product['image_url'])
        )
        
        print(f"INSERT結果: {result}")
        
        # 追加確認
        new_count = db_manager.execute_query(
            "SELECT COUNT(*) FROM products",
            fetch_one=True
        )
        print(f"追加後の商品数: {new_count}")
        
        # 追加した商品を検索
        added_product = db_manager.execute_query(
            "SELECT * FROM products WHERE name = %s",
            (test_product['name'],),
            fetch_one=True
        )
        
        if added_product:
            print("✓ 商品が正常に追加されました")
            print(f"追加された商品: {added_product}")
        else:
            print("✗ 商品が見つかりません")
            
        # 最新の商品10件を確認
        latest_products = db_manager.execute_query(
            "SELECT id, name, price, category FROM products ORDER BY id DESC LIMIT 10",
            fetch_all=True
        )
        
        print("\n=== 最新商品10件 ===")
        for product in latest_products:
            print(f"ID: {product.get('id')}, 名前: {product.get('name')}, 価格: {product.get('price')}, カテゴリ: {product.get('category')}")
            
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_insert()