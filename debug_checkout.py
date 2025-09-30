#!/usr/bin/env python3
"""
チェックアウト機能のデバッグスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils import safe_database_query

def test_cart_query():
    """カートクエリのテスト"""
    print("=== カートクエリデバッグ ===")
    
    # テストユーザーID（user1のID=2を想定）
    user_id = 2
    
    print(f"Testing with user_id: {user_id}")
    
    # 1. まずユーザーが存在するか確認
    print("\n1. ユーザー確認:")
    user_data = safe_database_query(
        "SELECT id, username FROM users WHERE id = %s", 
        (user_id,), 
        fetch_one=True
    )
    print(f"User data: {user_data}")
    print(f"Type: {type(user_data)}")
    
    # 2. カートデータの直接確認
    print("\n2. カート確認 (基本):")
    cart_basic = safe_database_query(
        "SELECT * FROM cart WHERE user_id = %s", 
        (user_id,), 
        fetch_all=True
    )
    print(f"Cart basic: {cart_basic}")
    print(f"Type: {type(cart_basic)}")
    
    # 3. 商品テーブル確認
    print("\n3. 商品テーブル確認:")
    products = safe_database_query(
        "SELECT id, name, price FROM products LIMIT 3", 
        fetch_all=True
    )
    print(f"Products: {products}")
    print(f"Type: {type(products)}")
    
    # 4. 問題のクエリを実行
    print("\n4. 問題のクエリテスト:")
    try:
        cart_items = safe_database_query("""
            SELECT c.id, p.name, p.price, c.quantity, p.id as product_id, p.image_url
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """, (user_id,), fetch_all=True)
        
        print(f"Cart items result: {cart_items}")
        print(f"Type: {type(cart_items)}")
        
        if cart_items:
            print(f"First item: {cart_items[0]}")
            print(f"First item type: {type(cart_items[0])}")
            
            if isinstance(cart_items[0], dict):
                print("Dict keys:", list(cart_items[0].keys()))
        
    except Exception as e:
        print(f"Error in query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cart_query()