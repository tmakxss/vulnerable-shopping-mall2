import urllib.request
import urllib.parse

def test_open_redirect():
    cookie = "user_id=6; username=test1001; is_admin=False; role=user; auth_token=eyJ1c2VyX2lkIjogNiwgInVzZXJuYW1lIjogInRlc3QxMDAxIiwgImlzX2FkbWluIjogZmFsc2UsICJyb2xlIjogInVzZXIifQ==; session=.eJxFjUEKwyAURK9SZu3CtJgEr9IEsfqlgkkhX1chd6-fLrp5M7xZzAmXiuc3MezzxK32ALcQiBkKS3to_xKmIAyzcOxmTikuzdy9FmMm4UT_bhLWa1XI7Hzc8g6bfGFSOD6FYNGYjn4g4XKEHX9995uslbgOWg-4vkqQM0Y.aNyEWw.WU_oe6wU6uh8fVnQR6l_FCRWEgA"
    
    test_payloads = [
        '//evil.com',
        '//evil.com/fake-login',
        'http://evil.com',
        'https://evil.com',
        '///evil.com',
        '/evil.com',
    ]
    
    print("=== Open Redirect テスト ===")
    
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
                def http_error_301(self, req, fp, code, msg, headers):
                    return fp
            
            opener = urllib.request.build_opener(NoRedirectHandler)
            response = opener.open(req)
            
            location = response.headers.get('Location')
            print(f"Location: {location}")
            
            # 実際にアクセスしてみる
            print(f"実際のリダイレクト先の動作:")
            if location:
                # 相対パスを絶対URLに変換
                if location.startswith('/'):
                    full_url = f"http://localhost:5000{location}"
                else:
                    full_url = location
                    
                print(f"フルURL: {full_url}")
                
                # ブラウザが実際にどう解釈するかシミュレート
                if location.startswith('/product///'):
                    print("→ ブラウザ解釈: 相対パス /product/... として処理")
                    print("→ 結果: 外部サイトへのリダイレクトは発生しない")
                elif location.startswith('/product//'):
                    print("→ ブラウザ解釈: 相対パス /product/... として処理") 
                    print("→ 結果: 外部サイトへのリダイレクトは発生しない")
                else:
                    print("→ ブラウザ解釈: 通常の相対パス")
                
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_open_redirect()