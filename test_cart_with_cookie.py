import urllib.request
import urllib.parse

# Cookieを使ってログイン済み状態でカート追加APIをテスト
def test_cart_xss_with_cookie():
    cookie = "user_id=6; username=test1001; is_admin=False; role=user; auth_token=eyJ1c2VyX2lkIjogNiwgInVzZXJuYW1lIjogInRlc3QxMDAxIiwgImlzX2FkbWluIjogZmFsc2UsICJyb2xlIjogInVzZXIifQ==; session=.eJyrVsosjk9Myc3MU7JKS8wpTtVRKsrPSVWyUiotTi1S0gFT8ZkpSlZmEHZeYi5ItiS1uMTQwMBQqRYA8MEVwA.aNx-1w.O7AR8BPtns4Kx0TkZEQWbu50oh4"
    
    test_payloads = [
        '"test',
        'javascript:alert(1)',
        'javascript:alert("XSS")',
        'javascript:alert(document.cookie)',
    ]
    
    print("=== カート追加 XSS テスト (Cookie認証) ===")
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n[テスト {i}] ペイロード: {repr(payload)}")
        
        # POSTデータの準備
        data = urllib.parse.urlencode({
            'product_id': payload,
            'quantity': '1'
        }).encode('utf-8')
        
        # リクエスト作成
        req = urllib.request.Request(
            "http://localhost:5000/cart/add",
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': cookie
            },
            method='POST'
        )
        
        try:
            # リクエスト送信 (リダイレクトを無効化)
            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def http_error_302(self, req, fp, code, msg, headers):
                    return fp
                def http_error_301(self, req, fp, code, msg, headers):
                    return fp
            
            opener = urllib.request.build_opener(NoRedirectHandler)
            response = opener.open(req)
            
            print(f"ステータス: {response.getcode()}")
            print(f"ヘッダー: {dict(response.headers)}")
            
            # Locationヘッダーの確認
            location = response.headers.get('Location')
            if location:
                print(f"Location: {location}")
                
                # XSSペイロードの検出
                if 'javascript:' in location.lower():
                    print("🔴 CRITICAL: JavaScript scheme detected in Location header!")
                elif 'alert' in location.lower():
                    print("🟠 WARNING: Alert function detected in Location!")
                elif payload in location:
                    print(f"🟡 INFO: Payload reflected in Location: {payload}")
                    
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_cart_xss_with_cookie()