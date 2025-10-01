from app.utils import safe_database_query

def check_users():
    try:
        print("=== ユーザー一覧確認 ===")
        
        users = safe_database_query(
            "SELECT id, username, password, email FROM users ORDER BY id",
            fetch_all=True,
            default_value=[]
        )
        
        if users:
            print(f"登録済みユーザー数: {len(users)}")
            for user in users:
                if isinstance(user, dict):
                    print(f"ID:{user.get('id')}, ユーザー名:'{user.get('username')}', パスワード:'{user.get('password')}', メール:'{user.get('email')}'")
        else:
            print("ユーザーが見つかりません")
            
        print("\n=== test1001 ユーザー検索 ===")
        test_user = safe_database_query(
            "SELECT * FROM users WHERE username = %s",
            ('test1001',),
            fetch_one=True
        )
        
        if test_user:
            print(f"test1001ユーザーが見つかりました: {test_user}")
        else:
            print("test1001ユーザーが見つかりません")
            
            # test1001ユーザーを作成
            print("\ntest1001ユーザーを作成中...")
            safe_database_query(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                ('test1001', 'test1234', 'test1001@example.com')
            )
            print("test1001ユーザーを作成しました")
            
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users()