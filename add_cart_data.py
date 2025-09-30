#!/usr/bin/env python3
"""
カートにテストデータを追加
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils import safe_database_query

def add_test_cart_data():
    """テスト用カートデータ追加"""
    print("=== カートテストデータ追加 ===")
    
    # user1 (id=2) にカートアイテム追加
    user_id = 2
    
    # 1. 既存カートデータ削除
    print("1. 既存カートクリア")
    result = safe_database_query(
        "DELETE FROM cart WHERE user_id = %s", 
        (user_id,)
    )
    print(f"Deleted rows: {result}")
    
    # 2. テストデータ追加
    print("2. テストデータ追加")
    
    test_items = [
        (user_id, 1, 1),  # ノートパソコン x1
        (user_id, 3, 2),  # Tシャツ x2
    ]
    
    for item in test_items:
        result = safe_database_query(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
            item
        )
        print(f"Added cart item: {item}, Result: {result}")
    
    # 3. 確認
    print("3. カート確認")
    cart_items = safe_database_query("""
        SELECT c.id, p.name, p.price, c.quantity, (p.price * c.quantity) as total
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = %s
    """, (user_id,), fetch_all=True)
    
    print(f"Cart items: {cart_items}")
    
    if cart_items:
        total = sum(float(item['total']) for item in cart_items)
        print(f"Total: {total}")

if __name__ == "__main__":
    add_test_cart_data()