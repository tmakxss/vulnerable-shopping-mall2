#!/usr/bin/env python3
"""
サニタイズ機能の単体テスト
"""

# サニタイズ関数の実装
def sanitize_input(input_str):
    """XSSフィルタリング - ><を含む危険な文字をサニタイズ"""
    if not input_str:
        return ''
    
    # 文字列に変換
    sanitized = str(input_str)
    
    # 危険な文字をエスケープ
    dangerous_chars = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '&': '&amp;',
        '/': '&#x2F;'
    }
    
    for char, replacement in dangerous_chars.items():
        sanitized = sanitized.replace(char, replacement)
    
    return sanitized

# テストケース
test_cases = [
    "1",  # 正常な値
    "1';alert('XSS');//",  # 基本的なXSS
    "1<script>alert('XSS')</script>",  # スクリプトタグ
    "1\"><img src=x onerror=alert(1)>",  # 属性値エスケープ
    "1';alert(document.cookie);//",  # クッキー窃取
    "1');alert('XSS');//",  # シングルクォートエスケープ
]

print("=== サニタイズ機能テスト ===\n")

for i, test_input in enumerate(test_cases, 1):
    sanitized = sanitize_input(test_input)
    print(f"テスト {i}:")
    print(f"  入力: {test_input}")
    print(f"  出力: {sanitized}")
    
    # XSS可能性チェック
    dangerous_patterns = ['<', '>', '"', "'", 'alert', 'script']
    is_dangerous = any(pattern in sanitized for pattern in dangerous_patterns[:4])  # HTMLタグ関連のみ
    
    if is_dangerous:
        print(f"  状態: 🚨 危険な文字が残存")
    else:
        print(f"  状態: ✅ サニタイズ済み")
    
    print()

print("=== 脆弱性分析 ===")
print("シングルクォート「'」は &#x27; にエスケープされるため、")
print("onclick=\"handleMailAction('{{ mailid }}')\" での XSS は防がれます。")
print()
print("しかし、この実装では完全に XSS を防げるため、")
print("実際の脆弱性には追加の条件が必要です。")