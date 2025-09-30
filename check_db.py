"""
データベース内容確認スクリプト
"""
from app.utils import safe_database_query

def check_database_contents():
    print("=== データベース内容確認 ===")
    
    # ユーザーデータ確認
    users = safe_database_query("SELECT id, email, created_at FROM users LIMIT 5", fetch_all=True, default_value=[])
    print(f"ユーザー数: {len(users) if users else 0}")
    if users:
        for user in users[:3]:
            print(f"  ユーザー: {user}")
    
    # 注文データ確認
    orders = safe_database_query("SELECT id, user_id, total_amount, status, created_at FROM orders LIMIT 5", fetch_all=True, default_value=[])
    print(f"\n注文数: {len(orders) if orders else 0}")
    if orders:
        for order in orders[:3]:
            print(f"  注文: {order}")
    
    # レビューデータ確認
    reviews = safe_database_query("SELECT id, user_id, product_id, rating, created_at FROM reviews LIMIT 5", fetch_all=True, default_value=[])
    print(f"\nレビュー数: {len(reviews) if reviews else 0}")
    if reviews:
        for review in reviews[:3]:
            print(f"  レビュー: {review}")

if __name__ == "__main__":
    check_database_contents()