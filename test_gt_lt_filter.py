#!/usr/bin/env python3
"""
><フィルタのテスト用スクリプト

このスクリプトでフィルタが正しく動作するかテストします
"""

def test_filter_manually():
    """手動テスト用の説明"""
    print("🔒 ><フィルタテスト")
    print("=" * 30)
    
    print("\n📝 テスト手順:")
    print("1. サーバーを起動: python run.py")
    print("2. ブラウザでログイン: http://localhost:5000/login")
    print("3. プロフィール編集: http://localhost:5000/user/profile/edit")
    print("4. ブラウザの開発者ツールを開く")
    print("5. フォーム送信時にHTTPリクエストを編集してテスト")
    
    print("\n🚫 ブロックされるべきペイロード:")
    blocked_payloads = [
        'address[<script>alert(1)</script>]=test',
        'address[>alert(1)<]=test',
        'address[<img src=x onerror=alert(1)>]=test',
        'address["><script>alert(1)</script>=test',
        'address[test>=value',
        'address[<test]=value',
        'address[test]=<script>alert(1)</script>',
        'address[test]=value>test',
    ]
    
    for i, payload in enumerate(blocked_payloads, 1):
        print(f"{i:2d}. {payload}")
    
    print("\n✅ 許可されるべきペイロード:")
    allowed_payloads = [
        'address["onmouseover=alert(1)]=test',
        'address["onfocus=alert(1)]=test', 
        'address["onclick=alert(1)]=test',
        'address["style="color:red"onmouseover="alert(1)]=test',
        'address[test"onmouseover"]=value',
        'address[normal_key]=normal_value',
    ]
    
    for i, payload in enumerate(allowed_payloads, 1):
        print(f"{i:2d}. {payload}")
    
    print("\n🔬 ブラウザでのテスト方法:")
    print("1. ネットワークタブでPOSTリクエストを確認")
    print("2. 'Edit and Resend' または類似機能を使用")
    print("3. Body部分に上記のペイロードを追加")
    print("4. 送信後にフラッシュメッセージを確認")
    print("   - ブロック: '不正な文字が検出されました' が表示")
    print("   - 許可: プロフィールページでデバッグ情報に反映")

def test_curl_examples():
    """cURLテスト例"""
    print("\n📋 cURLテスト例:")
    print("=" * 20)
    
    print("\n### ブロックされるペイロード")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/profile/edit \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "email=admin@example.com" \\')
    print('  --data-urlencode "address=東京都渋谷区" \\')
    print('  --data-urlencode "phone=090-1234-5678" \\')
    print('  --data-urlencode "address[<script>alert(1)</script>]=test"')
    print("```")
    print("期待結果: '不正な文字が検出されました' エラー")
    
    print("\n### 許可されるペイロード")
    print("```bash") 
    print("curl -X POST http://localhost:5000/user/profile/edit \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "email=admin@example.com" \\')
    print('  --data-urlencode "address=東京都渋谷区" \\')
    print('  --data-urlencode "phone=090-1234-5678" \\')
    print('  --data-urlencode \'address["onmouseover=alert(1)]=test\'')
    print("```")
    print("期待結果: プロフィールページでデバッグ情報に反映、XSS実行可能")

def test_filter_logic():
    """フィルタロジックの説明"""
    print("\n⚙️ フィルタロジック:")
    print("=" * 20)
    
    print("\n現在の実装:")
    print("```python")
    print("if '>' in param_key or '<' in param_key or '>' in value or '<' in value:")
    print("    flash('不正な文字が検出されました', 'error')")
    print("    continue")
    print("```")
    
    print("\nチェック対象:")
    print("1. address[KEY] の KEY 部分")
    print("2. address[key]=VALUE の VALUE 部分")
    print("3. '>' または '<' 文字の有無")
    
    print("\n許可される文字:")
    print("✅ \" (ダブルクォート)")
    print("✅ ' (シングルクォート)")
    print("✅ = (イコール)")
    print("✅ ( ) (括弧)")
    print("✅ 英数字、日本語")
    
    print("\nブロックされる文字:")
    print("❌ > (大なり)")
    print("❌ < (小なり)")

if __name__ == "__main__":
    test_filter_manually()
    test_curl_examples()
    test_filter_logic()
    
    print("\n" + "=" * 50)
    print("📖 このフィルタは教育目的で作成されています")
    print("🔒 実際のアプリケーションではより包括的な対策が必要です")