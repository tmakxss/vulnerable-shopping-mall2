"""
テストデータ作成スクリプト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils import safe_database_query

def create_test_data():
    app = create_app()
    with app.app_context():
        print("=== テストデータ作成 ===")
        
        # 注文データが存在するか確認
        existing_orders = safe_database_query("SELECT COUNT(*) as count FROM orders", fetch_one=True)
        print(f"既存注文数: {existing_orders.get('count', 0) if existing_orders else 0}")
        
        # 注文データがない場合は作成
        if not existing_orders or existing_orders.get('count', 0) == 0:
            print("テスト注文データを作成中...")
            
            # ユーザー1の注文
            safe_database_query("""
                INSERT INTO orders (user_id, total_amount, status, shipping_address, payment_method, created_at) 
                VALUES (1, 2500.00, '配送完了', '東京都渋谷区1-1-1', 'クレジットカード', NOW())
            """)
            
            # ユーザー2の注文
            safe_database_query("""
                INSERT INTO orders (user_id, total_amount, status, shipping_address, payment_method, created_at) 
                VALUES (2, 1800.00, '処理中', '大阪府大阪市2-2-2', '代金引換', NOW())
            """)
            
            print("テスト注文データを作成しました")
        
        # レビューデータが存在するか確認
        existing_reviews = safe_database_query("SELECT COUNT(*) as count FROM reviews", fetch_one=True)
        print(f"既存レビュー数: {existing_reviews.get('count', 0) if existing_reviews else 0}")
        
        # レビューデータがない場合は作成
        if not existing_reviews or existing_reviews.get('count', 0) == 0:
            print("テストレビューデータを作成中...")
            
            # 商品1のレビュー
            safe_database_query("""
                INSERT INTO reviews (user_id, product_id, rating, comment, created_at) 
                VALUES (1, 1, 5, '素晴らしい商品です！', NOW())
            """)
            
            # 商品2のレビュー
            safe_database_query("""
                INSERT INTO reviews (user_id, product_id, rating, comment, created_at) 
                VALUES (2, 1, 4, '良い商品でした', NOW())
            """)
            
            print("テストレビューデータを作成しました")
        
        # 最終確認
        orders = safe_database_query("SELECT COUNT(*) as count FROM orders", fetch_one=True)
        reviews = safe_database_query("SELECT COUNT(*) as count FROM reviews", fetch_one=True)
        
        print(f"\n最終確認:")
        print(f"  注文数: {orders.get('count', 0) if orders else 0}")
        print(f"  レビュー数: {reviews.get('count', 0) if reviews else 0}")

if __name__ == "__main__":
    create_test_data()