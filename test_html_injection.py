import urllib.request
import urllib.parse

def test_html_injection():
    cookie = "user_id=6; username=test1001; is_admin=False; role=user; auth_token=eyJ1c2VyX2lkIjogNiwgInVzZXJuYW1lIjogInRlc3QxMDAxIiwgImlzX2FkbWluIjogZmFsc2UsICJyb2xlIjogInVzZXIifQ==; session=.eJxFjUEKwyAURK9SZu3CtJgEr9IEsfqlgkkhX1chd6-fLrp5M7xZzAmXiuc3MezzxK32ALcQiBkKS3to_xKmIAyzcOxmTikuzdy9FmMm4UT_bhLWa1XI7Hzc8g6bfGFSOD6FYNGYjn4g4XKEHX9995uslbgOWg-4vkqQM0Y.aNyEWw.WU_oe6wU6uh8fVnQR6l_FCRWEgA"
    
    test_payloads = [
        '"><script>alert(1)</script>',
        '" onmouseover="alert(1)',
        '" href="javascript:alert(1)',
        '"><img src=x onerror=alert(1)>',
        '" onclick="alert(1)',
        '"><svg onload=alert(1)>',
        '" style="color:red" onmouseover="alert(1)',
    ]
    
    print("=== HTML Injection テスト ===")
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n[テスト {i}] ペイロード: {repr(payload)}")
        
        data = urllib.parse.urlencode({
            'product_id': payload,
            'quantity': '1'
        }).encode('utf-8')
        
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
            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def http_error_302(self, req, fp, code, msg, headers):
                    return fp
            
            opener = urllib.request.build_opener(NoRedirectHandler)
            response = opener.open(req)
            
            # レスポンス本文を取得
            content = response.read().decode('utf-8')
            
            print(f"ステータス: {response.getcode()}")
            location = response.headers.get('Location')
            if location:
                print(f"Location: {location}")
            
            # HTMLの確認
            if '<script>' in content:
                print("🔴 CRITICAL: <script> タグが検出されました!")
            elif 'onmouseover=' in content:
                print("🔴 CRITICAL: イベントハンドラが検出されました!")
            elif 'onerror=' in content:
                print("🔴 CRITICAL: onerror イベントが検出されました!")
            elif payload.replace('"', '&quot;') in content:
                print("🟡 INFO: ペイロードがHTMLエンコードされて反映")
            elif payload in content:
                print("🔴 CRITICAL: ペイロードが生のまま反映!")
            else:
                print("🟢 SAFE: ペイロードが適切に処理されている")
                
            # リダイレクトページの内容も確認
            print(f"HTML内容 (先頭500文字):")
            print(content[:500])
            print("---")
                
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_html_injection()