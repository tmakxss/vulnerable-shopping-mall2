#!/usr/bin/env python3
"""
Supabaseのテーブル構造とシーケンス確認・修正
"""
import os
import sys
from app.database import db_manager

def fix_supabase_sequence():
    """Supabaseのシーケンスを修正"""
    print("=== Supabaseシーケンス修正 ===")
    
    try:
        # 現在のテーブル構造を確認
        table_info = db_manager.execute_query(
            "SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name = 'products' ORDER BY ordinal_position",
            fetch_all=True
        )
        
        print("現在のproductsテーブル構造:")
        for col in table_info:
            print(f"  {col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        
        # 最大IDを確認
        max_id_result = db_manager.execute_query(
            "SELECT MAX(id) FROM products",
            fetch_one=True
        )
        max_id = max_id_result.get('max', 0) if max_id_result else 0
        print(f"\n現在の最大ID: {max_id}")
        
        # シーケンスの現在値を確認
        try:
            seq_info = db_manager.execute_query(
                "SELECT currval('products_id_seq') as current_val, last_value FROM products_id_seq",
                fetch_one=True
            )
            print(f"シーケンス現在値: {seq_info}")
        except Exception as e:
            print(f"シーケンス確認エラー: {e}")
        
        # シーケンスを最大ID+1にリセット
        if max_id:
            reset_val = max_id + 1
            reset_result = db_manager.execute_query(
                f"SELECT setval('products_id_seq', {reset_val}, false)"
            )
            print(f"シーケンスを{reset_val}にリセット: {reset_result}")
        
        # 再度シーケンス確認
        try:
            seq_info_after = db_manager.execute_query(
                "SELECT currval('products_id_seq') as current_val, last_value FROM products_id_seq",
                fetch_one=True
            )
            print(f"リセット後のシーケンス: {seq_info_after}")
        except Exception as e:
            print(f"リセット後シーケンス確認エラー: {e}")
        
        # テスト挿入
        test_name = f'シーケンステスト_{int(__import__("time").time())}'
        insert_result = db_manager.execute_query(
            "INSERT INTO products (name, description, price, stock, category, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (test_name, 'シーケンステスト', 999, 1, 'テスト', '/static/test.jpg')
        )
        
        print(f"\nテスト挿入結果: {insert_result}")
        
        if insert_result and insert_result > 0:
            # 挿入された商品を確認
            inserted_product = db_manager.execute_query(
                "SELECT * FROM products WHERE name = %s",
                (test_name,),
                fetch_one=True
            )
            print(f"✓ 挿入成功: {inserted_product}")
        else:
            print("✗ 挿入失敗")
            
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_supabase_sequence()