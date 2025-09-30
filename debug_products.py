#!/usr/bin/env python3
"""
商品データのデバッグスクリプト
"""

import os
from app.database import DatabaseManager

def debug_products():
    """商品データの構造を詳しく調査"""
    print("🔍 商品データ構造の詳細調査...")
    
    try:
        db = DatabaseManager()
        
        # 直接接続してデータを確認
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 商品データを取得
        cursor.execute("SELECT * FROM products LIMIT 1")
        result = cursor.fetchone()
        
        print(f"📊 取得結果のタイプ: {type(result)}")
        print(f"📊 取得結果の内容: {result}")
        print(f"📊 取得結果の長さ: {len(result) if result else 'None'}")
        
        # カラム情報を取得
        columns = [desc[0] for desc in cursor.description]
        print(f"📊 カラム情報: {columns}")
        print(f"📊 カラム数: {len(columns)}")
        
        if result:
            print("\n🔍 カラムとデータの対応:")
            for i, (col, val) in enumerate(zip(columns, result)):
                print(f"  {i}: {col} = {val}")
        
        # すべての商品を取得してテスト
        cursor.execute("SELECT * FROM products")
        all_results = cursor.fetchall()
        print(f"\n📊 全商品数: {len(all_results)}")
        
        if all_results:
            print(f"📊 最初の商品: {all_results[0]}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ デバッグエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_products()