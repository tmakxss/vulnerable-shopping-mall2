#!/usr/bin/env python3
"""
PostgreSQLクエリテスト
"""

from app.database import DatabaseManager

def test_postgresql_queries():
    """PostgreSQLクエリをテストする"""
    print("🔍 PostgreSQLクエリテスト開始...")
    
    try:
        db = DatabaseManager()
        
        # テスト1: 単純なクエリ
        print("テスト1: 全商品取得")
        products = db.execute_query("SELECT * FROM products LIMIT 2", fetch_all=True)
        print(f"結果: {len(products) if products else 0}件")
        if products:
            print(f"最初の商品: {products[0]}")
        
        # テスト2: パラメータ付きクエリ
        print("\nテスト2: ID指定商品取得")
        product = db.execute_query("SELECT * FROM products WHERE id = ?", (1,), fetch_one=True)
        print(f"結果: {product}")
        
        # テスト3: JOINクエリ
        print("\nテスト3: レビューJOIN")
        reviews = db.execute_query("""
            SELECT r.id, r.rating, r.comment, u.username 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            WHERE r.product_id = ? 
            LIMIT 2
        """, (1,), fetch_all=True)
        print(f"結果: {len(reviews) if reviews else 0}件")
        if reviews:
            print(f"最初のレビュー: {reviews[0]}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_postgresql_queries()