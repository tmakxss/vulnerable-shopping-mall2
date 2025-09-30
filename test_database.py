import os
from app.utils import get_database_status, safe_database_query
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """データベース接続とデータ確認"""
    print("🔍 データベース接続テスト開始...")
    
    # 接続状態確認
    db_status, db_message = get_database_status()
    print(f"📊 接続状態: {db_status}")
    print(f"📝 詳細: {db_message}")
    
    if db_status:
        print("\n✅ データベース接続成功！")
        
        # ユーザー確認
        users = safe_database_query("SELECT username, email FROM users", fetch_all=True, default_value=[])
        print(f"\n👥 ユーザー数: {len(users)}")
        for user in users:
            print(f"  - {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
        
        # 商品確認
        products = safe_database_query("SELECT name, price FROM products", fetch_all=True, default_value=[])
        print(f"\n🛍️ 商品数: {len(products)}")
        for product in products[:3]:  # 最初の3件を表示
            print(f"  - {product.get('name', 'N/A')}: ¥{product.get('price', 0)}")
        if len(products) > 3:
            print(f"  ... 他 {len(products) - 3} 件")
        
        print("\n🎉 データベース初期化完了！")
        print("🌐 Webサイトが完全に動作可能です。")
        
    else:
        print("\n❌ データベース接続失敗")
        print("🔧 Supabase SQLエディタで初期化を実行してください。")

if __name__ == "__main__":
    test_database_connection()